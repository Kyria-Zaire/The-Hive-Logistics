/** Road width, in px: a hairline with its marking, not an asphalt band. */
export const ROAD_WIDTH = 6;

/** One marking cycle: 44px of paint, 66px of gap. */
const DASH_ON = 44;
const DASH_PERIOD = 110;

/** How far MethodAnimated slides the vertical marking up. The track is sized from it. */
export const TRACK_TRAVEL = 2400;

type Orientation = "vertical" | "horizontal";

/**
 * The road as seen from directly above at night: nothing but the white centre marking.
 * The asphalt is the section's own black.
 *
 * Vertical, the marking lives in a track taller than the road so MethodAnimated can slide it
 * past — that is what reads as driving while the car holds still. It carries the class the
 * animation looks for. Horizontal, the car does the travelling instead, so the marking stays
 * put and is deliberately left out of that selector.
 */
export function MethodRoad({
  className,
  orientation = "vertical",
}: {
  className?: string;
  orientation?: Orientation;
}) {
  const horizontal = orientation === "horizontal";

  return (
    <div
      aria-hidden
      // No `relative` here: call sites position the road themselves, and a hardcoded
      // `relative` would override their `absolute`.
      // No background: the asphalt is the section itself. A tint here, however faint, showed
      // up as a grey band between the markings.
      className={`overflow-hidden ${className ?? ""}`.trim()}
    >
      <div
        className={
          horizontal
            ? "absolute inset-0"
            : "thl-method-road-track absolute inset-x-0 top-0"
        }
        style={{
          // Vertical: sized from the travel, not from the road — sized in percentages the
          // track ran out partway through the scroll and the marking vanished.
          ...(horizontal ? {} : { height: `calc(100% + ${TRACK_TRAVEL + 200}px)` }),
          backgroundImage: `linear-gradient(to ${horizontal ? "right" : "bottom"}, #ffffff 0 ${DASH_ON}px, transparent ${DASH_ON}px ${DASH_PERIOD}px)`,
          backgroundSize: horizontal
            ? `${DASH_PERIOD}px ${ROAD_WIDTH}px`
            : `${ROAD_WIDTH}px ${DASH_PERIOD}px`,
          backgroundRepeat: horizontal ? "repeat-x" : "repeat-y",
          backgroundPosition: horizontal ? "0 50%" : "50% 0",
          opacity: 0.85,
          willChange: horizontal ? undefined : "transform",
        }}
      />
    </div>
  );
}
