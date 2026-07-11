import { nextTick, onBeforeUnmount, onMounted } from 'vue'

const TAU = Math.PI * 2
const MAX_FRAME_DELTA = 0.04
const FIXED_TIMESTEP = 1 / 120
const MAX_PHYSICS_STEPS = 5
const COLLISION_SOLVER_ITERATIONS = 3
const COLLISION_RESTITUTION = 0.78
const FRICTION_COEFFICIENT = 0.1
const BOUNDARY_RESTITUTION = 0.68
const POSITION_SLOP = 1.5
const POSITION_CORRECTION_PERCENT = 0.28
const CONTACT_CLEAR_TIME = 0.12
const CONTACT_STUCK_TIME = 0.32
const CONTACT_STUCK_FRAMES = 24
const STUCK_COOLDOWN = 0.6
const NORMAL_HYSTERESIS_MIN = 2.5
const NORMAL_HYSTERESIS_RATIO = 0.18

function smoothstep(value) {
  const clamped = Math.min(Math.max(value, 0), 1)
  return clamped * clamped * (3 - 2 * clamped)
}

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
        amplitudeMinX: 8,
        amplitudeRangeX: 10,
        amplitudeMinY: 6,
        amplitudeRangeY: 7,
        speedScale: 0.72,
        rotationScale: 0.45,
        maxSpeed: 20,
        globalWeight: 0.24,
        collisionGlobalRatio: 0.3,
        globalStrength: 0.42,
        globalMaxForce: 1.5,
        globalMaxSpeed: 5,
        globalDriftSpeed: 1.1,
        localSteering: 0.65,
        localMaxForce: 1.8,
        freedomMinX: 12,
        freedomRangeX: 12,
        freedomMinY: 8,
        freedomRangeY: 9,
        edgeSteering: 1,
        edgeMaxForce: 4,
        collisionPadding: 6,
        avoidancePadding: 8,
        avoidanceStrength: 0.9,
        overscanX: 0.09,
        overscanY: 0.09,
        damping: 0.72,
        collisionDampingRatio: 0.58,
        collisionFreedomDuration: 0.8,
        bounceThreshold: 8,
        escapeSpeed: 0.45,
        escapeDuration: 0.65,
      }
    : {
        amplitudeScale: 1,
        amplitudeMinX: 20,
        amplitudeRangeX: 22,
        amplitudeMinY: 14,
        amplitudeRangeY: 16,
        speedScale: 1,
        rotationScale: 1,
        maxSpeed: 42,
        globalWeight: 0.26,
        collisionGlobalRatio: 0.25,
        globalStrength: 0.45,
        globalMaxForce: 2.4,
        globalMaxSpeed: 8,
        globalDriftSpeed: 1.8,
        localSteering: 0.72,
        localMaxForce: 3.2,
        freedomMinX: 30,
        freedomRangeX: 30,
        freedomMinY: 20,
        freedomRangeY: 22,
        edgeSteering: 1.1,
        edgeMaxForce: 8,
        collisionPadding: 9,
        avoidancePadding: 14,
        avoidanceStrength: 1.4,
        overscanX: 0.12,
        overscanY: 0.12,
        damping: 0.55,
        collisionDampingRatio: 0.55,
        collisionFreedomDuration: 1.1,
        bounceThreshold: 12,
        escapeSpeed: 0.75,
        escapeDuration: 0.85,
      }

  if (!reducedMotion) return motion

  return {
    ...motion,
    amplitudeScale: motion.amplitudeScale * 0.58,
    amplitudeMinX: motion.amplitudeMinX * 0.9,
    amplitudeRangeX: motion.amplitudeRangeX * 0.9,
    amplitudeMinY: motion.amplitudeMinY * 0.9,
    amplitudeRangeY: motion.amplitudeRangeY * 0.9,
    speedScale: motion.speedScale * 0.62,
    rotationScale: motion.rotationScale * 0.4,
    maxSpeed: motion.maxSpeed * 0.6,
    globalMaxForce: motion.globalMaxForce * 0.6,
    globalMaxSpeed: motion.globalMaxSpeed * 0.6,
    globalDriftSpeed: motion.globalDriftSpeed * 0.6,
    localMaxForce: motion.localMaxForce * 0.7,
    edgeMaxForce: motion.edgeMaxForce * 0.7,
    avoidanceStrength: motion.avoidanceStrength * 0.7,
    escapeSpeed: motion.escapeSpeed * 0.65,
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
  let accumulator = 0
  const contacts = new Map()

  function stop() {
    running = false
    lastTime = 0
    accumulator = 0

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
    const visualRect = element.getBoundingClientRect()
    const collisionWidth = visualRect.width
    const collisionHeight = visualRect.height
    if (
      !motionElement ||
      width <= 0 ||
      height <= 0 ||
      collisionWidth <= 0 ||
      collisionHeight <= 0
    ) {
      return null
    }

    const phaseSeed = seededValue(index, 1)
    const speedSeed = seededValue(index, 2)
    const amplitudeX = config.amplitudeMinX + seededValue(index, 3) * config.amplitudeRangeX
    const amplitudeY = config.amplitudeMinY + seededValue(index, 4) * config.amplitudeRangeY
    const freedomRadiusX = config.freedomMinX + seededValue(index, 8) * config.freedomRangeX
    const freedomRadiusY = config.freedomMinY + seededValue(index, 9) * config.freedomRangeY
    const mass = Math.min(1.5, 0.85 + (collisionWidth * collisionHeight) / 12000)
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
      mass,
      inverseMass: 1 / mass,
      outerX: previousBody?.outerX ?? 0,
      outerY: previousBody?.outerY ?? 0,
      outerVx: previousBody?.outerVx ?? 0,
      outerVy: previousBody?.outerVy ?? 0,
      outerA: previousBody?.outerA ?? 1,
      outerB: previousBody?.outerB ?? 0,
      outerC: previousBody?.outerC ?? 0,
      outerD: previousBody?.outerD ?? 1,
      width,
      height,
      collisionWidth,
      collisionHeight,
      padding: config.collisionPadding,
      amplitudeX,
      amplitudeY,
      freedomRadiusX,
      freedomRadiusY,
      phase: phaseSeed * TAU,
      phaseY: seededValue(index, 6) * TAU,
      speed: (0.3 + speedSeed * 0.2) * config.speedScale,
      verticalSpeedRatio: 0.68 + seededValue(index, 7) * 0.16,
      collisionFreedomUntil: previousBody?.collisionFreedomUntil ?? 0,
      rotationAmplitude: (0.55 + seededValue(index, 5) * 0.95) * config.rotationScale,
    }
  }

  function resetInvalidBody(body) {
    if (
      Number.isFinite(body.x) &&
      Number.isFinite(body.y) &&
      Number.isFinite(body.vx) &&
      Number.isFinite(body.vy) &&
      Number.isFinite(body.outerX) &&
      Number.isFinite(body.outerY) &&
      Number.isFinite(body.outerVx) &&
      Number.isFinite(body.outerVy) &&
      Number.isFinite(body.outerA) &&
      Number.isFinite(body.outerB) &&
      Number.isFinite(body.outerC) &&
      Number.isFinite(body.outerD) &&
      Number.isFinite(body.collisionFreedomUntil) &&
      Number.isFinite(body.mass) &&
      Number.isFinite(body.inverseMass) &&
      body.inverseMass > 0
    ) {
      return
    }

    body.x = 0
    body.y = 0
    body.vx = 0
    body.vy = 0
    body.outerX = 0
    body.outerY = 0
    body.outerVx = 0
    body.outerVy = 0
    body.outerA = 1
    body.outerB = 0
    body.outerC = 0
    body.outerD = 1
    body.collisionFreedomUntil = 0
    body.mass = 1
    body.inverseMass = 1
  }

  function updateOuterMotion(delta = 0) {
    bodies.forEach((body) => {
      const previousX = body.outerX
      const previousY = body.outerY
      const transform = getComputedStyle(body.element).transform
      let nextX = 0
      let nextY = 0

      if (transform && transform !== 'none') {
        try {
          const matrix = new DOMMatrixReadOnly(transform)
          nextX = Number.isFinite(matrix.m41) ? matrix.m41 : 0
          nextY = Number.isFinite(matrix.m42) ? matrix.m42 : 0
          body.outerA = Number.isFinite(matrix.a) ? matrix.a : 1
          body.outerB = Number.isFinite(matrix.b) ? matrix.b : 0
          body.outerC = Number.isFinite(matrix.c) ? matrix.c : 0
          body.outerD = Number.isFinite(matrix.d) ? matrix.d : 1
        } catch {
          nextX = 0
          nextY = 0
          body.outerA = 1
          body.outerB = 0
          body.outerC = 0
          body.outerD = 1
        }
      }

      body.outerX = nextX
      body.outerY = nextY
      body.outerVx = delta > 0 ? (nextX - previousX) / delta : 0
      body.outerVy = delta > 0 ? (nextY - previousY) / delta : 0
    })
  }

  function clampBodySpeed(body) {
    const speed = Math.hypot(body.vx, body.vy)
    if (speed <= config.maxSpeed || speed === 0) return

    const scale = config.maxSpeed / speed
    body.vx *= scale
    body.vy *= scale
  }

  function clampVector(x, y, maximum) {
    const length = Math.hypot(x, y)
    if (!Number.isFinite(length) || length === 0) return [0, 0]
    if (length <= maximum) return [x, y]

    const scale = maximum / length
    return [x * scale, y * scale]
  }

  function getCollisionFreedom(body) {
    const remaining = Math.max(0, body.collisionFreedomUntil - elapsed)
    return smoothstep(remaining / config.collisionFreedomDuration)
  }

  function beginCollisionFreedom(first, second) {
    const freedomUntil = elapsed + config.collisionFreedomDuration
    first.collisionFreedomUntil = Math.max(first.collisionFreedomUntil, freedomUntil)
    second.collisionFreedomUntil = Math.max(second.collisionFreedomUntil, freedomUntil)
  }

  function getBodyBounds(body) {
    const centerX = body.baseX + body.x + body.width / 2
    const centerY = body.baseY + body.y + body.height / 2

    return {
      left: centerX - body.collisionWidth / 2 - body.padding,
      right: centerX + body.collisionWidth / 2 + body.padding,
      top: centerY - body.collisionHeight / 2 - body.padding,
      bottom: centerY + body.collisionHeight / 2 + body.padding,
      centerX,
      centerY,
    }
  }

  function getPairKey(first, second) {
    return first.id < second.id ? `${first.id}:${second.id}` : `${second.id}:${first.id}`
  }

  function createContact(first, second) {
    const key = getPairKey(first, second)
    const escapeSeed = [...key].reduce((total, character) => total + character.charCodeAt(0), 0)
    const contact = {
      firstId: first.id,
      secondId: second.id,
      contactTime: 0,
      contactFrames: 0,
      separationTime: 0,
      separationFrames: 0,
      stalledTime: 0,
      lastPenetration: Infinity,
      normalX: 0,
      normalY: 0,
      escapeSign: escapeSeed % 2 === 0 ? 1 : -1,
      escapeUntil: 0,
      avoidance: 0,
      cooldownUntil: 0,
      lastCollisionTime: 0,
    }
    contacts.set(key, contact)
    return contact
  }

  function suppressContactSteering(body, steeringX, steeringY) {
    let adjustedX = steeringX
    let adjustedY = steeringY

    contacts.forEach((contact) => {
      if (contact.firstId !== body.id && contact.secondId !== body.id) return

      const escapeRemaining = Math.max(0, contact.escapeUntil - elapsed)
      const escapeRecovery = Math.min(escapeRemaining / config.escapeDuration, 1)
      const avoidanceSuppression = contact.avoidance * 0.42
      const suppression = Math.max(avoidanceSuppression, 0.92 * escapeRecovery)
      const direction = contact.firstId === body.id ? 1 : -1
      const towardX = contact.normalX * direction
      const towardY = contact.normalY * direction
      const normalSteering = adjustedX * towardX + adjustedY * towardY

      if (normalSteering > 0) {
        adjustedX -= towardX * normalSteering * suppression
        adjustedY -= towardY * normalSteering * suppression
      }
    })

    return [adjustedX, adjustedY]
  }

  function containBody(body) {
    if (!world) return

    const bounds = getBodyBounds(body)

    if (bounds.left < world.left) {
      body.x += world.left - bounds.left
      if (body.vx < 0) body.vx = -body.vx * BOUNDARY_RESTITUTION
    } else if (bounds.right > world.right) {
      body.x -= bounds.right - world.right
      if (body.vx > 0) body.vx = -body.vx * BOUNDARY_RESTITUTION
    }

    if (bounds.top < world.top) {
      body.y += world.top - bounds.top
      if (body.vy < 0) body.vy = -body.vy * BOUNDARY_RESTITUTION
    } else if (bounds.bottom > world.bottom) {
      body.y -= bounds.bottom - world.bottom
      if (body.vy > 0) body.vy = -body.vy * BOUNDARY_RESTITUTION
    }
  }

  function resolveCollision(first, second, delta = 0, applyImpulse = true) {
    resetInvalidBody(first)
    resetInvalidBody(second)

    const firstBounds = getBodyBounds(first)
    const secondBounds = getBodyBounds(second)
    const overlapX =
      Math.min(firstBounds.right, secondBounds.right) -
      Math.max(firstBounds.left, secondBounds.left)
    const overlapY =
      Math.min(firstBounds.bottom, secondBounds.bottom) -
      Math.max(firstBounds.top, secondBounds.top)

    const contactKey = getPairKey(first, second)
    let contact = contacts.get(contactKey)

    if (overlapX <= 0 || overlapY <= 0) {
      const avoidanceOverlapX = overlapX + config.avoidancePadding * 2
      const avoidanceOverlapY = overlapY + config.avoidancePadding * 2

      if (applyImpulse && avoidanceOverlapX > 0 && avoidanceOverlapY > 0) {
        contact ??= createContact(first, second)
        contact.separationTime += delta
        contact.separationFrames += 1
        contact.contactFrames = 0
        contact.stalledTime = 0
        contact.lastPenetration = Infinity

        const keepEscapeNormal =
          elapsed < contact.escapeUntil && (contact.normalX || contact.normalY)
        if (!keepEscapeNormal) {
          const useHorizontal = avoidanceOverlapX < avoidanceOverlapY
          const centerDeltaX = secondBounds.centerX - firstBounds.centerX
          const centerDeltaY = secondBounds.centerY - firstBounds.centerY
          contact.normalX = useHorizontal
            ? Math.abs(centerDeltaX) > 0.01
              ? Math.sign(centerDeltaX)
              : contact.escapeSign
            : 0
          contact.normalY = useHorizontal
            ? 0
            : Math.abs(centerDeltaY) > 0.01
              ? Math.sign(centerDeltaY)
              : contact.escapeSign
        }
        contact.avoidance = Math.min(
          1,
          Math.max(0, Math.min(avoidanceOverlapX, avoidanceOverlapY) / config.avoidancePadding)
        )

        const avoidanceForce = config.avoidanceStrength * contact.avoidance * delta
        first.vx -= contact.normalX * avoidanceForce
        first.vy -= contact.normalY * avoidanceForce
        second.vx += contact.normalX * avoidanceForce
        second.vy += contact.normalY * avoidanceForce
        clampBodySpeed(first)
        clampBodySpeed(second)
        return false
      }

      if (contact && applyImpulse) {
        contact.separationTime += delta
        contact.separationFrames += 1
        contact.avoidance = 0
        if (contact.separationTime >= CONTACT_CLEAR_TIME) {
          contacts.delete(contactKey)
        }
      }
      return false
    }

    if (applyImpulse) {
      contact ??= createContact(first, second)
      contact.contactTime += delta
      contact.contactFrames += 1
      contact.separationTime = 0
      contact.separationFrames = 0
      contact.avoidance = 1
    }

    let normalX = 0
    let normalY = 0
    let penetration = overlapY

    const horizontalHysteresis = Math.max(NORMAL_HYSTERESIS_MIN, overlapX * NORMAL_HYSTERESIS_RATIO)
    const verticalHysteresis = Math.max(NORMAL_HYSTERESIS_MIN, overlapY * NORMAL_HYSTERESIS_RATIO)
    const keepHorizontalNormal = contact?.normalX && overlapY >= overlapX - horizontalHysteresis
    const keepVerticalNormal = contact?.normalY && overlapX >= overlapY - verticalHysteresis

    if (keepHorizontalNormal) {
      normalX = contact.normalX
      penetration = overlapX
    } else if (keepVerticalNormal) {
      normalY = contact.normalY
    } else if (overlapX < overlapY) {
      const centerDeltaX = secondBounds.centerX - firstBounds.centerX
      normalX = Math.abs(centerDeltaX) > 0.01 ? Math.sign(centerDeltaX) : contact?.escapeSign || 1
      penetration = overlapX
    } else {
      const centerDeltaY = secondBounds.centerY - firstBounds.centerY
      normalY = Math.abs(centerDeltaY) > 0.01 ? Math.sign(centerDeltaY) : contact?.escapeSign || 1
    }

    if (contact) {
      contact.normalX = normalX
      contact.normalY = normalY
    }

    const inverseMassSum = first.inverseMass + second.inverseMass
    const correction =
      (Math.max(penetration - POSITION_SLOP, 0) / inverseMassSum) * POSITION_CORRECTION_PERCENT
    first.x -= normalX * correction * first.inverseMass
    first.y -= normalY * correction * first.inverseMass
    second.x += normalX * correction * second.inverseMass
    second.y += normalY * correction * second.inverseMass

    if (applyImpulse) {
      const relativeVelocity = (second.vx - first.vx) * normalX + (second.vy - first.vy) * normalY

      const penetrationImprovement = contact.lastPenetration - penetration
      const lowRelativeSpeed = Math.abs(relativeVelocity) < 6
      contact.stalledTime =
        lowRelativeSpeed && penetrationImprovement < 0.2
          ? contact.stalledTime + delta
          : Math.max(0, contact.stalledTime - delta * 0.5)
      contact.lastPenetration = penetration

      if (relativeVelocity < 0) {
        const restitution =
          Math.abs(relativeVelocity) >= config.bounceThreshold ? COLLISION_RESTITUTION : 0
        const normalImpulse = (-(1 + restitution) * relativeVelocity) / inverseMassSum
        first.vx -= normalImpulse * normalX * first.inverseMass
        first.vy -= normalImpulse * normalY * first.inverseMass
        second.vx += normalImpulse * normalX * second.inverseMass
        second.vy += normalImpulse * normalY * second.inverseMass

        const tangentX = -normalY
        const tangentY = normalX
        const relativeTangentVelocity =
          (second.vx - first.vx) * tangentX + (second.vy - first.vy) * tangentY
        const rawFrictionImpulse = -relativeTangentVelocity / inverseMassSum
        const maximumFrictionImpulse = normalImpulse * FRICTION_COEFFICIENT
        const frictionImpulse = Math.min(
          Math.max(rawFrictionImpulse, -maximumFrictionImpulse),
          maximumFrictionImpulse
        )
        first.vx -= frictionImpulse * tangentX * first.inverseMass
        first.vy -= frictionImpulse * tangentY * first.inverseMass
        second.vx += frictionImpulse * tangentX * second.inverseMass
        second.vy += frictionImpulse * tangentY * second.inverseMass

        if (restitution > 0) {
          contact.escapeUntil = elapsed + config.escapeDuration
          beginCollisionFreedom(first, second)
          contact.lastCollisionTime = elapsed
        }
      }

      if (
        contact.contactFrames >= CONTACT_STUCK_FRAMES &&
        contact.stalledTime >= CONTACT_STUCK_TIME &&
        elapsed >= contact.cooldownUntil
      ) {
        const tangentX = -normalY * contact.escapeSign
        const tangentY = normalX * contact.escapeSign
        first.vx += tangentX * config.escapeSpeed * first.inverseMass
        first.vy += tangentY * config.escapeSpeed * first.inverseMass
        second.vx -= tangentX * config.escapeSpeed * second.inverseMass
        second.vy -= tangentY * config.escapeSpeed * second.inverseMass
        contact.stalledTime = 0
        contact.escapeUntil = elapsed + config.escapeDuration
        beginCollisionFreedom(first, second)
        contact.cooldownUntil = elapsed + STUCK_COOLDOWN
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
          separated =
            resolveCollision(bodies[firstIndex], bodies[secondIndex], 0, false) || separated
        }
      }

      bodies.forEach(containBody)
      if (!separated) break
    }
  }

  function renderBodies() {
    bodies.forEach((body) => {
      resetInvalidBody(body)
      const determinant = body.outerA * body.outerD - body.outerB * body.outerC
      const compensatedX = body.x - body.outerX
      const compensatedY = body.y - body.outerY
      const localX =
        Math.abs(determinant) > 0.0001
          ? (body.outerD * compensatedX - body.outerC * compensatedY) / determinant
          : compensatedX
      const localY =
        Math.abs(determinant) > 0.0001
          ? (-body.outerB * compensatedX + body.outerA * compensatedY) / determinant
          : compensatedY
      const rotation =
        Math.sin(elapsed * body.speed * 0.83 + body.phase * 1.19) * body.rotationAmplitude
      body.motionElement.style.transform = `translate3d(${localX.toFixed(2)}px, ${localY.toFixed(
        2
      )}px, 0) rotate(${rotation.toFixed(2)}deg)`
    })
  }

  function updateBodies(delta) {
    bodies.forEach((body) => {
      resetInvalidBody(body)
      const targetX = Math.sin(elapsed * body.speed + body.phase) * body.amplitudeX
      const targetY =
        Math.sin(elapsed * body.speed * body.verticalSpeedRatio + body.phaseY) * body.amplitudeY
      const freedom = getCollisionFreedom(body)
      const globalControl = 1 - freedom * (1 - config.collisionGlobalRatio)
      const globalWeight = config.globalWeight * globalControl

      const fallbackGlobalX = Math.sin(elapsed * 0.18 + body.phase * 0.08)
      const fallbackGlobalY = Math.cos(elapsed * 0.15 + body.phaseY * 0.06) * 0.65
      const [desiredGlobalVx, desiredGlobalVy] = clampVector(
        body.outerVx * globalWeight + fallbackGlobalX * config.globalDriftSpeed,
        body.outerVy * globalWeight + fallbackGlobalY * config.globalDriftSpeed,
        config.globalMaxSpeed
      )
      let [globalForceX, globalForceY] = clampVector(
        (desiredGlobalVx - body.vx) * config.globalStrength * globalControl,
        (desiredGlobalVy - body.vy) * config.globalStrength * globalControl,
        config.globalMaxForce * globalControl
      )

      const adjustedGlobalForce = suppressContactSteering(body, globalForceX, globalForceY)
      globalForceX = adjustedGlobalForce[0]
      globalForceY = adjustedGlobalForce[1]

      let [localForceX, localForceY] = suppressContactSteering(
        body,
        (targetX - body.x) * config.localSteering,
        (targetY - body.y) * config.localSteering
      )
      const limitedLocalForce = clampVector(localForceX, localForceY, config.localMaxForce)
      localForceX = limitedLocalForce[0]
      localForceY = limitedLocalForce[1]

      const overrunX = Math.max(0, Math.abs(body.x) - body.freedomRadiusX)
      const overrunY = Math.max(0, Math.abs(body.y) - body.freedomRadiusY)
      const edgeBlendX = smoothstep(overrunX / Math.max(body.freedomRadiusX * 0.3, 1))
      const edgeBlendY = smoothstep(overrunY / Math.max(body.freedomRadiusY * 0.3, 1))
      const [edgeForceX, edgeForceY] = clampVector(
        -Math.sign(body.x) * overrunX * config.edgeSteering * edgeBlendX,
        -Math.sign(body.y) * overrunY * config.edgeSteering * edgeBlendY,
        config.edgeMaxForce
      )
      localForceX += edgeForceX
      localForceY += edgeForceY

      const dampingStrength = config.damping * (1 - freedom * (1 - config.collisionDampingRatio))
      const damping = Math.exp(-dampingStrength * delta)

      body.vx = (body.vx + (globalForceX + localForceX) * delta) * damping
      body.vy = (body.vy + (globalForceY + localForceY) * delta) * damping
      clampBodySpeed(body)
      body.x += body.vx * delta
      body.y += body.vy * delta
    })

    for (let iteration = 0; iteration < COLLISION_SOLVER_ITERATIONS; iteration += 1) {
      for (let firstIndex = 0; firstIndex < bodies.length; firstIndex += 1) {
        for (let secondIndex = firstIndex + 1; secondIndex < bodies.length; secondIndex += 1) {
          resolveCollision(bodies[firstIndex], bodies[secondIndex], delta, iteration === 0)
        }
      }
    }

    bodies.forEach((body) => {
      containBody(body)
      clampBodySpeed(body)
      resetInvalidBody(body)
    })
  }

  function animate(timestamp) {
    if (!running) return

    if (!lastTime) lastTime = timestamp
    const rawDelta = Number.isFinite(timestamp) ? (timestamp - lastTime) / 1000 : 0
    const delta = Math.min(Math.max(Number.isFinite(rawDelta) ? rawDelta : 0, 0), MAX_FRAME_DELTA)
    lastTime = timestamp
    updateOuterMotion(delta)
    accumulator = Math.min(accumulator + delta, FIXED_TIMESTEP * MAX_PHYSICS_STEPS)

    let physicsSteps = 0
    while (accumulator >= FIXED_TIMESTEP && physicsSteps < MAX_PHYSICS_STEPS) {
      elapsed += FIXED_TIMESTEP
      updateBodies(FIXED_TIMESTEP)
      accumulator -= FIXED_TIMESTEP
      physicsSteps += 1
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
    contacts.clear()
    accumulator = 0
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
    updateOuterMotion()
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
    contacts.clear()
    bodies = []
  })
}
