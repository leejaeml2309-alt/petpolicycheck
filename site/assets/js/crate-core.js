/*!
 * PetPolicyCheck · crate-core.js
 * Reusable crate / carrier check logic (Pet Travel Planner, future crate calculator).
 *
 * Rules (see /workspace/planner/DATA.md):
 *  - Only figures stated by the airline record are used. Nothing is estimated,
 *    rounded into another unit or converted (kg is never turned into lb, cm never into in).
 *  - A null limit means "not stated by the official source" and yields status "unknown".
 *  - Carrier dimensions are verbatim text in the current data layer, so the dimension
 *    check returns "manual" (side-by-side comparison) unless a structured
 *    {l, w, h, unit} limit object is supplied by a future data layer.
 *
 * Works as a browser global (window.PPCCrate) and as a CommonJS module.
 */
(function (root, factory) {
  var api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.PPCCrate = api;
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var WEIGHT_UNITS = ['kg', 'lb'];
  var LENGTH_UNITS = ['cm', 'in'];

  function num(v) {
    if (v === null || v === undefined || v === '') return null;
    var n = typeof v === 'number' ? v : parseFloat(String(v).replace(',', '.'));
    return isFinite(n) && n >= 0 ? n : null;
  }

  /** Does the stated weight limit include the carrier? true / false / null (unclear). */
  function limitIncludesCarrier(asStated) {
    if (!asStated) return null;
    var s = String(asStated).toLowerCase();
    if (/includ(ing|es|e) (the )?(carrier|kennel|container|pet)|pet \+ carrier|pet and carrier|carrier and (the )?pet|total weight|combined/.test(s)) return true;
    if (/the pet must weigh|pets? weighing|animal must weigh/.test(s)) return false;
    return null;
  }

  /** Structured stated limit in the requested unit, or null. Never converts. */
  function statedLimit(weightObj, unit) {
    if (!weightObj || WEIGHT_UNITS.indexOf(unit) < 0) return null;
    var v = weightObj[unit];
    return typeof v === 'number' ? v : null;
  }

  /**
   * Cabin weight check.
   * @param {object} airline  planner airline record
   * @param {object} input    {petWeight, carrierWeight, unit:'kg'|'lb'}
   * @returns {object} {status:'within'|'over'|'depends'|'unknown'|'other-unit'|'no-input',
   *                    limit, unit, otherUnit, includesCarrier, total, pet, asStated, scope}
   */
  function checkCabinWeight(airline, input) {
    var w = (airline && airline.cabin_max_weight) || {};
    var unit = input && WEIGHT_UNITS.indexOf(input.unit) >= 0 ? input.unit : 'kg';
    var other = unit === 'kg' ? 'lb' : 'kg';
    var pet = num(input && input.petWeight);
    var carrier = num(input && input.carrierWeight);
    var total = pet !== null ? pet + (carrier || 0) : null;
    var res = {
      status: 'unknown', unit: unit, limit: statedLimit(w, unit), otherUnit: null,
      includesCarrier: limitIncludesCarrier(w.as_stated), pet: pet, carrier: carrier,
      total: total, carrierEntered: carrier !== null,
      asStated: w.as_stated || null, scope: w.scope || null
    };
    if (res.limit === null) {
      var o = statedLimit(w, other);
      if (o !== null) { res.status = 'other-unit'; res.otherUnit = { value: o, unit: other }; }
      return res;
    }
    if (pet === null) { res.status = 'no-input'; return res; }
    if (res.includesCarrier === false) {
      res.status = pet <= res.limit ? 'within' : 'over';
      res.compared = 'pet';
      return res;
    }
    if (res.includesCarrier === true) {
      if (!res.carrierEntered) {
        res.status = pet > res.limit ? 'over' : 'depends';
        res.compared = 'pet-only-entered';
        return res;
      }
      res.status = total <= res.limit ? 'within' : 'over';
      res.compared = 'total';
      return res;
    }
    /* Unclear wording: within only if even the total fits, over only if the pet alone exceeds. */
    if (total <= res.limit) { res.status = 'within'; res.compared = 'total'; }
    else if (pet > res.limit) { res.status = 'over'; res.compared = 'pet'; }
    else { res.status = 'depends'; res.compared = 'unclear'; }
    return res;
  }

  /**
   * Dimension check. The current data layer only has verbatim dimension text,
   * so without a structured limit this returns status "manual".
   * @param {object|null} limit  optional structured {l,w,h,unit} from a future data layer
   * @param {object} crate       {l,w,h,unit}
   */
  function checkDimensions(limit, crate, asStated) {
    var c = {
      l: num(crate && crate.l), w: num(crate && crate.w), h: num(crate && crate.h),
      unit: crate && LENGTH_UNITS.indexOf(crate.unit) >= 0 ? crate.unit : 'cm'
    };
    var entered = c.l !== null && c.w !== null && c.h !== null;
    var res = { status: 'manual', crate: c, entered: entered, asStated: asStated || null, over: [] };
    if (!asStated && !limit) res.status = 'unknown';
    if (!entered) { if (res.status !== 'unknown') res.status = 'no-input'; return res; }
    if (!limit || typeof limit.l !== 'number' || typeof limit.w !== 'number' || typeof limit.h !== 'number') return res;
    if (limit.unit !== c.unit) { res.status = 'other-unit'; return res; }
    /* Axis-order independent: compare sorted sides (largest with largest). */
    var a = [c.l, c.w, c.h].sort(function (x, y) { return y - x; });
    var b = [limit.l, limit.w, limit.h].sort(function (x, y) { return y - x; });
    for (var i = 0; i < 3; i++) if (a[i] > b[i]) res.over.push({ side: i, crate: a[i], limit: b[i] });
    res.status = res.over.length ? 'over' : 'within';
    return res;
  }

  /** Species check against species_allowed. */
  function checkSpecies(airline, species) {
    var list = airline && airline.species_allowed;
    if (list === null || list === undefined) return { status: 'unknown', list: null };
    if (!list.length) return { status: 'none', list: list };
    var key = { dog: 'dogs', cat: 'cats' }[species] || species;
    return { status: list.indexOf(key) >= 0 ? 'listed' : 'not-listed', list: list };
  }

  return {
    version: '2026-11-18',
    num: num,
    limitIncludesCarrier: limitIncludesCarrier,
    statedLimit: statedLimit,
    checkCabinWeight: checkCabinWeight,
    checkDimensions: checkDimensions,
    checkSpecies: checkSpecies,
    WEIGHT_UNITS: WEIGHT_UNITS,
    LENGTH_UNITS: LENGTH_UNITS
  };
});
