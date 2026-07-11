import { nextTick, onBeforeUnmount, onMounted } from 'vue'

const TAU = Math.PI * 2
const MAX_FRAME_DELTA = 0.04
const MAX_SUBSTEP = 0.012
const COLLISION_RESTITUTION = 0.76
const BOUNDARY_RESTITUTION = 0.68

function seededValue(index, offset = 0) {
  const value = Math.sin((index + 1) * 12.9898 + offset * 78.233) * 43758.5453
  return value - Math.floor(value)
}

function getMotionConfig() {
  const mobile = window.matchMedia('(max-width: 920px)').matches
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

  const motion = mobile
    ? {
        amplitudeScale: 0.52,
        speedScale: 0.72,
        rotationScale: 0.45,
        maxSpeed: 20,
        collisionPadding: 6,
        overscanX: 0.09,
        overscanY: 0.09,
        steering: 2.1,
        damping: 1.7,
      }
    : {
        amplitudeScale: 1,
        speedScale: 1,
        rotationScale: 1,
        maxSpeed: 42,
        collisionPadding: 9,
        overscanX: 0.12,
        overscanY: 0.12,
        steering: 2.35,
        damping: 1.45,
      }

  if (!reducedMotion) return motion

  return {
    ...motion,
    amplitudeScale: motion.amplitudeScale * 0.58,
    speedScale: motion.speedScale * 0.62,
    rotationScale: motion.rotationScale * 0.4,
    maxSpeed: motion.maxSpeed * 0.6,
  }
}

export function useFormulaPhysics(formulaCloud) {
  let bodies = []
  let world = null
  let config = null
  let frameId = 0
  let resizeFrameId = 0
  let resizeObserver = null
  let reducedMotionQuery = null
  let running = false
  let mounted = false
  let lastTime = 0
  let elapsed = 0

  function stop() {
    running = false
    lastTime = 0

    if (frameId) {
      cancelAnimationFrame(frameId)
      frameId = 0
    }
  }

  function clearFormulaTransforms() {
    const cloud = formulaCloud.value
    if (!cloud) return

    cloud.classList.remove('formula-physics-active')
    cloud.querySelectorAll('.formula-local-body').forEach((element) => {
      element.style.removeProperty('transform')
    })
  }

  function measureWorld(cloud) {
    const board = cloud.parentElement
    if (!board) return null

    const cloudRect = cloud.getBoundingClientRect()
    const boardRect = board.getBoundingClientRect()

    return {
      left: boardRect.left - cloudRect.left - boardRect.width * config.overscanX,
      right: boardRect.right - cloudRect.left + boardRect.width * config.overscanX,
      top: boardRect.top - cloudRect.top - boardRect.height * config.overscanY,
      bottom: boardRect.bottom - cloudRect.top + boardRect.height * config.overscanY,
    }
  }

  function createBody(element, index, previousBody) {
    const motionElement = element.querySelector('.formula-local-body')
    const width = element.offsetWidth
    const height = element.offsetHeight
    if (!motionElement || width <= 0 || height <= 0) return null

    const phaseSeed = seededValue(index, 1)
    const speedSeed = seededValue(index, 2)
    const amplitudeX = (9 + seededValue(index, 3) * 12) * config.amplitudeScale
    const amplitudeY = (6 + seededValue(index, 4) * 10) * config.amplitudeScale
    const baseX = element.offsetLeft
    const baseY = element.offsetTop

    return {
      id: element.className.match(/formula-\d+/)?.[0] ?? `formula-${index + 1}`,
      element,
      motionElement,
      baseX,
      baseY,
      x: previousBody ? previousBody.baseX + previousBody.x - baseX : 0,
      y: previousBody ? previousBody.baseY + previousBody.y - baseY : 0,
      vx: previousBody?.vx ?? 0,
      vy: previousBody?.vy ?? 0,
      width,
      height,
      padding: config.collisionPadding,
      amplitudeX,
      amplitudeY,
      phase: phaseSeed * TAU,
      speed: (0.3 + speedSeed * 0.2) * config.speedScale,
      rotationAmplitude: (0.55 + seededValue(index, 5) * 0.95) * config.rotationScale,
    }
  }

  function resetInvalidBody(body) {
    if (
      Number.isFinite(body.x) &&
      Number.isFinite(body.y) &&
      Number.isFinite(body.vx) &&
      Number.isFinite(body.vy)
    ) {
      return
    }

    body.x = 0
    body.y = 0
    body.vx = 0
    body.vy = 0
  }

  function clampBodySpeed(body) {
    const speed = Math.hypot(body.vx, body.vy)
    if (speed <= config.maxSpeed || speed === 0) return

    const scale = config.maxSpeed / speed
    body.vx *= scale
    body.vy *= scale
  }

  function containBody(body) {
    if (!world) return

    const minX = world.left
    const maxX = Math.max(minX, world.right - body.width)
    const minY = world.top
    const maxY = Math.max(minY, world.bottom - body.height)
    const absoluteX = body.baseX + body.x
    const absoluteY = body.baseY + body.y

    if (absoluteX < minX) {
      body.x += minX - absoluteX
      body.vx = Math.abs(body.vx) * BOUNDARY_RESTITUTION
    } else if (absoluteX > maxX) {
      body.x -= absoluteX - maxX
      body.vx = -Math.abs(body.vx) * BOUNDARY_RESTITUTION
    }

    if (absoluteY < minY) {
      body.y += minY - absoluteY
      body.vy = Math.abs(body.vy) * BOUNDARY_RESTITUTION
    } else if (absoluteY > maxY) {
      body.y -= absoluteY - maxY
      body.vy = -Math.abs(body.vy) * BOUNDARY_RESTITUTION
    }
  }

  function resolveCollision(first, second, applyImpulse = true) {
    resetInvalidBody(first)
    resetInvalidBody(second)

    const firstLeft = first.baseX + first.x - first.padding
    const firstTop = first.baseY + first.y - first.padding
    const secondLeft = second.baseX + second.x - second.padding
    const secondTop = second.baseY + second.y - second.padding
    const overlapX =
      Math.min(
        firstLeft + first.width + first.padding * 2,
        secondLeft + second.width + second.padding * 2
      ) - Math.max(firstLeft, secondLeft)
    const overlapY =
      Math.min(
        firstTop + first.height + first.padding * 2,
        secondTop + second.height + second.padding * 2
      ) - Math.max(firstTop, secondTop)

    if (overlapX <= 0 || overlapY <= 0) return false

    const firstCenterX = firstLeft + (first.width + first.padding * 2) / 2
    const firstCenterY = firstTop + (first.height + first.padding * 2) / 2
    const secondCenterX = secondLeft + (second.width + second.padding * 2) / 2
    const secondCenterY = secondTop + (second.height + second.padding * 2) / 2
    let normalX = 0
    let normalY = 0
    let penetration = overlapY

    if (overlapX < overlapY) {
      normalX = secondCenterX >= firstCenterX ? 1 : -1
      penetration = overlapX
    } else {
      normalY = secondCenterY >= firstCenterY ? 1 : -1
    }

    const correction = (penetration + 0.5) * 0.52
    first.x -= normalX * correction
    first.y -= normalY * correction
    second.x += normalX * correction
    second.y += normalY * correction

    if (applyImpulse) {
      const relativeVelocity = (second.vx - first.vx) * normalX + (second.vy - first.vy) * normalY

      if (relativeVelocity < 0) {
        const impulse = (-(1 + COLLISION_RESTITUTION) * relativeVelocity) / 2
        first.vx -= impulse * normalX
        first.vy -= impulse * normalY
        second.vx += impulse * normalX
        second.vy += impulse * normalY
      }
    }

    clampBodySpeed(first)
    clampBodySpeed(second)
    return true
  }

  function separateBodies(iterations = 4) {
    for (let iteration = 0; iteration < iterations; iteration += 1) {
      let separated = false

      for (let firstIndex = 0; firstIndex < bodies.length; firstIndex += 1) {
        for (let secondIndex = firstIndex + 1; secondIndex < bodies.length; secondIndex += 1) {
          separated = resolveCollision(bodies[firstIndex], bodies[secondIndex], false) || separated
        }
      }

      bodies.forEach(containBody)
      if (!separated) break
    }
  }

  function renderBodies() {
    bodies.forEach((body) => {
      resetInvalidBody(body)
      const rotation =
        Math.sin(elapsed * body.speed * 0.83 + body.phase * 1.19) * body.rotationAmplitude
      body.motionElement.style.transform = `translate3d(${body.x.toFixed(2)}px, ${body.y.toFixed(
        2
      )}px, 0) rotate(${rotation.toFixed(2)}deg)`
    })
  }

  function updateBodies(delta) {
    const sharedX = Math.sin(elapsed * 0.22) * 2.4 * config.amplitudeScale
    const sharedY = Math.cos(elapsed * 0.17) * 1.8 * config.amplitudeScale

    bodies.forEach((body) => {
      resetInvalidBody(body)
      const targetX = sharedX + Math.sin(elapsed * body.speed + body.phase) * body.amplitudeX
      const targetY =
        sharedY + Math.sin(elapsed * body.speed * 0.73 + body.phase * 1.37) * body.amplitudeY
      const damping = Math.exp(-config.damping * delta)

      body.vx = (body.vx + (targetX - body.x) * config.steering * delta) * damping
      body.vy = (body.vy + (targetY - body.y) * config.steering * delta) * damping
      clampBodySpeed(body)
      body.x += body.vx * delta
      body.y += body.vy * delta
    })

    for (let firstIndex = 0; firstIndex < bodies.length; firstIndex += 1) {
      for (let secondIndex = firstIndex + 1; secondIndex < bodies.length; secondIndex += 1) {
        resolveCollision(bodies[firstIndex], bodies[secondIndex])
      }
    }

    bodies.forEach(containBody)
  }

  function animate(timestamp) {
    if (!running) return

    if (!lastTime) lastTime = timestamp
    const rawDelta = Number.isFinite(timestamp) ? (timestamp - lastTime) / 1000 : 0
    const delta = Math.min(Math.max(Number.isFinite(rawDelta) ? rawDelta : 0, 0), MAX_FRAME_DELTA)
    lastTime = timestamp
    elapsed += delta

    const substeps = Math.max(1, Math.min(4, Math.ceil(delta / MAX_SUBSTEP)))
    const stepDelta = delta / substeps

    for (let step = 0; step < substeps; step += 1) {
      updateBodies(stepDelta)
    }

    renderBodies()
    frameId = requestAnimationFrame(animate)
  }

  function start() {
    if (running || document.hidden || bodies.length === 0) {
      return
    }

    running = true
    lastTime = 0
    frameId = requestAnimationFrame(animate)
  }

  function refreshBodies() {
    const cloud = formulaCloud.value
    if (!cloud || !mounted) return

    const previousBodies = new Map(bodies.map((body) => [body.element, body]))
    const elements = Array.from(cloud.querySelectorAll('.theory-card'))
    config = getMotionConfig()
    world = measureWorld(cloud)

    elements.forEach((element) => {
      if (getComputedStyle(element).display === 'none') {
        element.style.removeProperty('transform')
      }
    })

    bodies = elements
      .filter((element) => getComputedStyle(element).display !== 'none')
      .map((element, index) => createBody(element, index, previousBodies.get(element)))
      .filter(Boolean)

    if (bodies.length === 0) {
      scheduleRefresh()
      return
    }

    cloud.classList.add('formula-physics-active')
    separateBodies()
    renderBodies()
    start()
  }

  function scheduleRefresh() {
    if (resizeFrameId) cancelAnimationFrame(resizeFrameId)
    resizeFrameId = requestAnimationFrame(() => {
      resizeFrameId = 0
      refreshBodies()
    })
  }

  function handleVisibilityChange() {
    if (document.hidden) {
      stop()
    } else {
      start()
    }
  }

  function handleReducedMotionChange() {
    refreshBodies()
  }

  onMounted(async () => {
    mounted = true
    await nextTick()
    if (!mounted) return

    reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    reducedMotionQuery.addEventListener('change', handleReducedMotionChange)
    document.addEventListener('visibilitychange', handleVisibilityChange)
    window.addEventListener('resize', scheduleRefresh, { passive: true })

    resizeObserver = new ResizeObserver(scheduleRefresh)
    if (formulaCloud.value) {
      resizeObserver.observe(formulaCloud.value)
      formulaCloud.value.querySelectorAll('.theory-card').forEach((element) => {
        resizeObserver.observe(element)
      })
    }

    scheduleRefresh()
    document.fonts?.ready.then(() => {
      if (mounted) scheduleRefresh()
    })
  })

  onBeforeUnmount(() => {
    mounted = false
    stop()

    if (resizeFrameId) {
      cancelAnimationFrame(resizeFrameId)
      resizeFrameId = 0
    }

    resizeObserver?.disconnect()
    reducedMotionQuery?.removeEventListener('change', handleReducedMotionChange)
    document.removeEventListener('visibilitychange', handleVisibilityChange)
    window.removeEventListener('resize', scheduleRefresh)
    clearFormulaTransforms()
    bodies = []
  })
}
