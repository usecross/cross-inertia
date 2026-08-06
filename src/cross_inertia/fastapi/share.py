import functools
import inspect
from typing import Annotated, Any, Callable, TypeVar, get_args, get_origin

from starlette.requests import Request

F = TypeVar("F", bound=Callable[..., Any])


def _resolved_annotations(fn: F) -> dict[str, Any]:
    """Resolve postponed annotations independently.

    A missing return-only type must not prevent FastAPI from seeing resolvable
    parameter types such as ``Request``, ``date``, or ``Annotated``.
    """

    annotations = inspect.get_annotations(fn, eval_str=False)
    resolved: dict[str, Any] = {}
    for name, annotation in annotations.items():
        if not isinstance(annotation, str):
            resolved[name] = annotation
            continue
        try:
            resolved[name] = eval(annotation, fn.__globals__)
        except (NameError, TypeError, SyntaxError):
            resolved[name] = annotation
    return resolved


def _is_request_annotation(annotation: Any) -> bool:
    if annotation is Request:
        return True
    return (
        get_origin(annotation) is Annotated
        and bool(get_args(annotation))
        and get_args(annotation)[0] is Request
    )


def _find_request_parameter(
    sig: inspect.Signature,
    annotations: dict[str, Any],
) -> str | None:
    """Return the existing Starlette request parameter, if any.

    ``from __future__ import annotations`` stores annotations as strings, so an
    identity check against ``Request`` is not sufficient.  Keep the conventional
    parameter name as a fallback for annotations that cannot be resolved.
    """

    for name, parameter in sig.parameters.items():
        annotation = annotations.get(name, parameter.annotation)
        if _is_request_annotation(annotation):
            return name
        if name == "request":
            return name

    return None


def _merge_shared(request: Request, result: dict[str, Any] | None) -> None:
    if not result:
        return

    existing = getattr(request.state, "inertia_shared", {})

    request.state.inertia_shared = {**existing, **result}


def inertia_share(fn: F) -> F:
    """Mark a function as an Inertia shared data provider.

    The return value is merged into ``request.state.inertia_shared``.
    If the function doesn't declare ``request: Request``, one is auto-injected.
    """

    sig: inspect.Signature = inspect.signature(fn)
    annotations = _resolved_annotations(fn)

    request_parameter = _find_request_parameter(sig, annotations)
    has_request = request_parameter is not None
    is_async: bool = inspect.iscoroutinefunction(fn)

    if is_async:

        @functools.wraps(fn)
        async def async_wrapper(**kwargs: Any) -> None:
            request: Request = kwargs[request_parameter or "request"]
            if has_request:
                result = await fn(**kwargs)
            else:
                result = await fn(**{k: v for k, v in kwargs.items() if k != "request"})
            _merge_shared(request, result)

        wrapper: F = async_wrapper  # type: ignore[assignment]
    else:

        @functools.wraps(fn)
        def sync_wrapper(**kwargs: Any) -> None:
            request: Request = kwargs[request_parameter or "request"]
            if has_request:
                result = fn(**kwargs)
            else:
                result = fn(**{k: v for k, v in kwargs.items() if k != "request"})
            _merge_shared(request, result)

        wrapper = sync_wrapper  # type: ignore[assignment]

    params: list[inspect.Parameter] = []
    for name, parameter in sig.parameters.items():
        annotation = annotations.get(name, parameter.annotation)
        if name == request_parameter and not _is_request_annotation(annotation):
            annotation = Request
        params.append(parameter.replace(annotation=annotation))

    if not has_request:
        request_param = inspect.Parameter(
            "request",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Request,
        )

        params.insert(0, request_param)

    wrapper.__signature__ = sig.replace(  # type: ignore[attr-defined]
        parameters=params,
        return_annotation=annotations.get("return", sig.return_annotation),
    )

    return wrapper
