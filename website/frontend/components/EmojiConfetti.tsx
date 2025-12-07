import { useState, useCallback } from 'react'

interface ConfettiParticle {
  id: number
  x: number
  y: number
  angle: number
  velocity: number
  spin: number
  scale: number
}

export function EmojiConfetti({ children, emoji }: { children: React.ReactNode; emoji: string }) {
  const [particles, setParticles] = useState<ConfettiParticle[]>([])
  const [isActive, setIsActive] = useState(false)

  const triggerBurst = useCallback(() => {
    if (isActive) return
    setIsActive(true)

    const newParticles: ConfettiParticle[] = []
    const count = 15

    for (let i = 0; i < count; i++) {
      // Burst in all directions from center
      const angle = (i / count) * Math.PI * 2 + (Math.random() - 0.5) * 0.5
      newParticles.push({
        id: Date.now() + i,
        x: 50, // Start from center
        y: 50,
        angle,
        velocity: 80 + Math.random() * 60, // Distance to travel
        spin: (Math.random() - 0.5) * 720, // Random rotation
        scale: 0.7 + Math.random() * 0.6,
      })
    }
    setParticles(newParticles)

    setTimeout(() => {
      setParticles([])
      setIsActive(false)
    }, 1000)
  }, [isActive])

  return (
    <span
      className="relative inline-block"
      onMouseEnter={triggerBurst}
    >
      {children}
      <span className="absolute inset-0 pointer-events-none overflow-visible">
        {particles.map((p) => {
          const endX = p.x + Math.cos(p.angle) * p.velocity
          const endY = p.y + Math.sin(p.angle) * p.velocity

          return (
            <span
              key={p.id}
              className="absolute"
              style={{
                left: '50%',
                top: '50%',
                fontSize: `${p.scale}rem`,
                transform: 'translate(-50%, -50%)',
                animation: `emojiConfettiBurst 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards`,
                '--end-x': `${(endX - 50)}px`,
                '--end-y': `${(endY - 50)}px`,
                '--spin': `${p.spin}deg`,
              } as React.CSSProperties}
            >
              {emoji}
            </span>
          )
        })}
      </span>
    </span>
  )
}
