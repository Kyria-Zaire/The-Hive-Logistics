/**
 * French number formatting, shared by the server render and the count-up that replaces it.
 *
 * One function for both on purpose: the figure is written into the HTML on the server and
 * rewritten on every frame by the animation, and if the two disagreed on the thousands
 * separator the number would jump the moment the count reached its target. French groups with
 * a narrow no-break space (U+202F), not the plain space the copy used to carry.
 */
const frenchNumber = new Intl.NumberFormat("fr-FR");

export function formatFr(value: number): string {
  return frenchNumber.format(Math.round(value));
}
