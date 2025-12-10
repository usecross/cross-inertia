import { EmojiConfetti, type HomeFeature } from '@usecross/docs'

export function CustomFeatures({ features }: { features: HomeFeature[] }) {
  // Inject EmojiConfetti into the first feature's description
  const enhancedFeatures = features.map((feature, index) => {
    if (index === 0 && typeof feature.description === 'string' && feature.description.includes('GraphQL')) {
      return {
        ...feature,
        description: (
          <>
            Skip building a separate <EmojiConfetti emoji="⚡">REST</EmojiConfetti> or <EmojiConfetti emoji="🍓">GraphQL</EmojiConfetti> API. Your controllers return page components directly.
          </>
        ),
      }
    }
    return feature
  })

  return (
    <section className="border-t border-gray-200">
      <div className="grid grid-cols-12">
        {/* Section header */}
        <div className="col-span-12 lg:col-span-4 p-4 lg:p-10 border-b lg:border-b-0 lg:border-r border-gray-200">
          <div className="text-sm font-mono uppercase tracking-widest text-gray-500 mb-4">
            Why Cross-Inertia
          </div>
          <h2 className="text-4xl lg:text-5xl font-bold tracking-tight">
            Modern
            <br />
            Monoliths
          </h2>
        </div>

        {/* Features grid */}
        <div className="col-span-12 lg:col-span-8 grid grid-cols-1 sm:grid-cols-2">
          {enhancedFeatures.map((feature, index) => (
            <div
              key={index}
              className={`p-4 lg:p-10 border-b sm:border-b border-gray-200 ${
                index % 2 === 0 ? 'sm:border-r' : ''
              } ${index >= enhancedFeatures.length - 2 ? 'sm:border-b-0' : ''} ${
                index === enhancedFeatures.length - 1 && enhancedFeatures.length % 2 === 1 ? 'border-b-0' : ''
              }`}
            >
              <div className="text-6xl font-bold text-primary-500 mb-4">
                {String(index + 1).padStart(2, '0')}
              </div>
              <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
              <p className="text-gray-600">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
