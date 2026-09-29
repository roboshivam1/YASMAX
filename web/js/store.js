/*
 * File: web/js/store.js
 *
 * Holds the latest engine snapshot and tells panels when it changes.
 *
 * This is the whole "state management" of YASMAX, on purpose. There is no
 * framework: the engine already owns all real state, and the UI only has
 * to redraw from the newest snapshot (docs/ARCHITECTURE.md §6).
 *
 * Usage
 * -----
 *     const store = createStore();
 *     store.subscribe((snap, prev) => redrawRegisters(snap, prev));
 *     store.applyReply(await engine.call("reset_all_registers"));
 *
 * Subscribers get the previous snapshot too, so a panel can update only
 * the cells that changed. Updating in place keeps scroll position and
 * focus, which a full redraw would lose.
 */

export function createStore() {
  let current = null;
  const subscribers = new Set();

  function set(snapshot) {
    if (!snapshot) return;
    const previous = current;
    current = snapshot;
    for (const fn of subscribers) fn(current, previous);
  }

  return {
    /** The latest snapshot, or null before boot. */
    get: () => current,

    set,

    /** Take the snapshot out of an engine reply (if it has one) and publish it. */
    applyReply(reply) {
      set(reply?.snapshot);
      return reply;
    },

    /**
     * Register fn(snapshot, previousSnapshot). If a snapshot already
     * exists, fn runs once immediately so the panel draws right away.
     * Returns an unsubscribe function.
     */
    subscribe(fn) {
      subscribers.add(fn);
      if (current) fn(current, null);
      return () => subscribers.delete(fn);
    },
  };
}
