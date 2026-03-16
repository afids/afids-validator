"""Anatomical descriptions and placement guidance for the 32 AFIDs landmarks."""

# Keys match the abbreviation used as the attribute name on the Afids object
# (i.e., EXPECTED_DESCS[i][-1]).
LANDMARK_INFO = {
    "AC": {
        "full_name": "Anterior Commissure",
        "description": (
            "A white matter tract connecting the two temporal lobes, crossing "
            "the midline at the base of the septum pellucidum."
        ),
        "key_features": (
            "On a midsagittal slice, look for a small hyperintense (bright) "
            "bundle just anterior to the columns of the fornix and inferior "
            "to the genu of the corpus callosum. The AC sits directly at the "
            "midline where the lamina terminalis meets the anterior "
            "commissure itself."
        ),
        "common_mistakes": (
            "Placing too posteriorly (confusing with the fornix columns) or "
            "too superiorly (landing on the genu of CC). Stay at the "
            "midline — any lateral offset is an error."
        ),
    },
    "PC": {
        "full_name": "Posterior Commissure",
        "description": (
            "A small white matter tract at the dorsal aspect of the cerebral "
            "aqueduct, marking the posterior boundary of the third ventricle."
        ),
        "key_features": (
            "On midsagittal: find the aqueduct of Sylvius and trace it "
            "superiorly to where it opens into the third ventricle. The PC "
            "lies at this junction, just superior to the superior colliculi "
            "and inferior to the habenular commissure."
        ),
        "common_mistakes": (
            "Placing on the habenular commissure (too superior) or on the "
            "superior colliculi (too inferior and posterior)."
        ),
    },
    "ICS": {
        "full_name": "Infracollicular Sulcus",
        "description": (
            "The sulcus immediately inferior to the inferior colliculi on "
            "the posterior surface of the midbrain."
        ),
        "key_features": (
            "On sagittal: identify the quadrigeminal plate (four bumps on "
            "the dorsal midbrain). The ICS is the groove just below the "
            "inferior colliculi, where the midbrain meets the superior "
            "medullary velum."
        ),
        "common_mistakes": (
            "Confusing with the intercollicular sulcus (the groove between "
            "superior and inferior colliculi). The ICS is inferior to both "
            "pairs of colliculi."
        ),
    },
    "PMJ": {
        "full_name": "Pontomedullary Junction",
        "description": (
            "The anatomical boundary between the pons and the medulla "
            "oblongata on the ventral brainstem."
        ),
        "key_features": (
            "On sagittal: the ventral pons has a characteristic bulge "
            "(the basis pontis). The PMJ is where this bulge ends and "
            "the more tapered medulla begins — look for the change in "
            "ventral contour. On axial: the disappearance of the "
            "transverse pontine fibres."
        ),
        "common_mistakes": (
            "Placing too superiorly (within the pons) or too inferiorly "
            "(within the medulla). The junction is often subtler on "
            "standard T1 — use multiple planes."
        ),
    },
    "SIPF": {
        "full_name": "Superior Interpeduncular Fossa",
        "description": (
            "The apex of the interpeduncular fossa, the CSF-filled space "
            "between the cerebral peduncles on the ventral midbrain."
        ),
        "key_features": (
            "On coronal or axial: the interpeduncular fossa appears as a "
            "dark (CSF) inverted V between the two cerebral peduncles. "
            "Place at the most superior tip of this space, at the level "
            "of the mammillary bodies."
        ),
        "common_mistakes": (
            "Placing at the midpoint of the fossa rather than its most "
            "superior extent. Confirm on sagittal that placement is "
            "superior to the pons."
        ),
    },
    "RSLMS": {
        "full_name": "Right Superior Lateral Midbrain Sulcus",
        "description": (
            "The sulcus at the superior lateral margin of the right "
            "midbrain, at the midbrain–thalamus interface."
        ),
        "key_features": (
            "On axial at the level of the superior colliculi: identify "
            "the lateral margin of the midbrain. The RSLMS is the groove "
            "where the superior aspect of the right midbrain meets the "
            "overlying thalamus/pulvinar."
        ),
        "common_mistakes": (
            "Placing on the midbrain surface rather than in the sulcal "
            "fundus. Confirm the left–right placement by ensuring "
            "symmetry with LSLMS."
        ),
    },
    "LSLMS": {
        "full_name": "Left Superior Lateral Midbrain Sulcus",
        "description": (
            "The sulcus at the superior lateral margin of the left "
            "midbrain, at the midbrain–thalamus interface."
        ),
        "key_features": (
            "Mirror of RSLMS. On axial at the level of the superior "
            "colliculi: the groove where the superior aspect of the left "
            "midbrain meets the overlying thalamus/pulvinar."
        ),
        "common_mistakes": (
            "Placing on the midbrain surface rather than in the sulcal "
            "fundus. Check bilateral symmetry with RSLMS."
        ),
    },
    "RILMS": {
        "full_name": "Right Inferior Lateral Midbrain Sulcus",
        "description": (
            "The sulcus at the inferior lateral margin of the right "
            "midbrain, at the midbrain–pons interface."
        ),
        "key_features": (
            "On axial at the level of the inferior colliculi or superior "
            "pons: the groove at the lateral inferior margin of the right "
            "midbrain, where it blends with the superior pons."
        ),
        "common_mistakes": (
            "Confusing with RSLMS — RILMS is more inferior and anterior. "
            "Use coronal plane to confirm the inferior extent."
        ),
    },
    "LILMS": {
        "full_name": "Left Inferior Lateral Midbrain Sulcus",
        "description": (
            "The sulcus at the inferior lateral margin of the left "
            "midbrain, at the midbrain–pons interface."
        ),
        "key_features": (
            "Mirror of RILMS. On axial at the level of the inferior "
            "colliculi: the groove at the lateral inferior margin of the "
            "left midbrain."
        ),
        "common_mistakes": (
            "Confusing with LSLMS — LILMS is more inferior. Confirm "
            "bilateral symmetry with RILMS."
        ),
    },
    "CUL": {
        "full_name": "Culmen",
        "description": (
            "The most superior point of the anterior lobe of the "
            "cerebellar vermis (lobule IV/V)."
        ),
        "key_features": (
            "On midsagittal: follow the superior surface of the cerebellum "
            "to its highest midline point. The culmen is the peak of the "
            "anterior vermis, immediately posterior to the primary fissure."
        ),
        "common_mistakes": (
            "Placing on the declive (posterior to the primary fissure) "
            "or on a lateral cerebellar hemisphere rather than the midline "
            "vermis."
        ),
    },
    "IMS": {
        "full_name": "Intermammillary Sulcus",
        "description": (
            "The midpoint of the sulcus between the two mammillary bodies "
            "on the inferior hypothalamus."
        ),
        "key_features": (
            "On coronal: identify the two round mammillary bodies just "
            "posterior to the tuber cinereum. The IMS is placed at the "
            "midpoint of the groove between them. On axial: two bright "
            "dots separated by a narrow sulcus at the floor of the "
            "diencephalon."
        ),
        "common_mistakes": (
            "Placing on one of the mammillary bodies rather than the "
            "sulcus between them. The IMS must be at the midline."
        ),
    },
    "RMB": {
        "full_name": "Right Mammillary Body",
        "description": (
            "The right mammillary body, a posterior hypothalamic nucleus "
            "involved in memory circuits."
        ),
        "key_features": (
            "On coronal: the right of the two round structures at the "
            "floor of the diencephalon, just anterior to the midbrain. "
            "On axial: appears as a bright dot just right of midline, "
            "posterior to the tuber cinereum."
        ),
        "common_mistakes": (
            "Placing on the IMS midpoint instead of the centre of the "
            "right body, or landing too superiorly in the hypothalamus."
        ),
    },
    "LMB": {
        "full_name": "Left Mammillary Body",
        "description": (
            "The left mammillary body, a posterior hypothalamic nucleus "
            "involved in memory circuits."
        ),
        "key_features": (
            "Mirror of RMB. On coronal: the left of the two round "
            "structures at the floor of the diencephalon."
        ),
        "common_mistakes": (
            "Placing on the IMS midpoint instead of the centre of the "
            "left body, or landing too superiorly in the hypothalamus."
        ),
    },
    "PG": {
        "full_name": "Pineal Gland",
        "description": (
            "A small midline neuroendocrine gland at the posterior roof "
            "of the third ventricle."
        ),
        "key_features": (
            "On midsagittal: posterior to the habenular commissure and "
            "superior to the superior colliculi. Often appears as a "
            "calcified (hyperdense on CT, variable on MRI) nodule. "
            "Place at the centre of the gland."
        ),
        "common_mistakes": (
            "Confusing with the habenular commissure (too anterior/superior) "
            "or placing on the superior colliculi (too inferior). The PG "
            "sits in the pineal recess, not on the quadrigeminal plate."
        ),
    },
    "RLVAC": {
        "full_name": "Right Lateral Ventricle at AC",
        "description": (
            "The most lateral point of the right lateral ventricle body "
            "at the coronal level of the anterior commissure."
        ),
        "key_features": (
            "On a coronal slice through the AC: find the body of the "
            "right lateral ventricle and place at its most lateral "
            "extent. The septum pellucidum separates left and right."
        ),
        "common_mistakes": (
            "Using the wrong coronal level — must be at the AC, not "
            "anterior or posterior to it. Confirm AC location on sagittal "
            "first, then switch to coronal."
        ),
    },
    "LLVAC": {
        "full_name": "Left Lateral Ventricle at AC",
        "description": (
            "The most lateral point of the left lateral ventricle body "
            "at the coronal level of the anterior commissure."
        ),
        "key_features": (
            "Mirror of RLVAC. On coronal at AC level: most lateral "
            "extent of the left lateral ventricle body."
        ),
        "common_mistakes": (
            "Same as RLVAC — confirm AC level on sagittal first. "
            "Check bilateral symmetry."
        ),
    },
    "RLVPC": {
        "full_name": "Right Lateral Ventricle at PC",
        "description": (
            "The most lateral point of the right lateral ventricle body "
            "at the coronal level of the posterior commissure."
        ),
        "key_features": (
            "On a coronal slice through the PC: the right lateral "
            "ventricle body at its most lateral point. The ventricle "
            "is typically narrower here than at the AC level."
        ),
        "common_mistakes": (
            "Confusing the PC level with the AC level. Identify PC on "
            "sagittal first (dorsal aqueduct opening), then move to "
            "coronal."
        ),
    },
    "LLVPC": {
        "full_name": "Left Lateral Ventricle at PC",
        "description": (
            "The most lateral point of the left lateral ventricle body "
            "at the coronal level of the posterior commissure."
        ),
        "key_features": (
            "Mirror of RLVPC. Coronal at PC level: most lateral extent "
            "of the left lateral ventricle."
        ),
        "common_mistakes": (
            "Same as RLVPC — confirm PC level before switching planes. "
            "Check bilateral symmetry."
        ),
    },
    "GENU": {
        "full_name": "Genu of the Corpus Callosum",
        "description": (
            "The anteriormost bend of the corpus callosum where it "
            "curves inferiorly toward the rostrum."
        ),
        "key_features": (
            "On midsagittal: the anterior end of the corpus callosum "
            "where the fibres curve forward and downward. Place at the "
            "most anterior and inferior point of this bend, not at the "
            "superior surface."
        ),
        "common_mistakes": (
            "Placing on the superior surface of the CC rather than the "
            "anterior-inferior curve, or confusing with the rostrum "
            "(the thin portion below the genu)."
        ),
    },
    "SPLE": {
        "full_name": "Splenium of the Corpus Callosum",
        "description": (
            "The posterior thickened end of the corpus callosum, "
            "connecting the occipital and parietal lobes."
        ),
        "key_features": (
            "On midsagittal: the bulbous posterior terminus of the "
            "corpus callosum. Place at the most posterior point of "
            "the splenium, at the midline."
        ),
        "common_mistakes": (
            "Placing too anteriorly (on the posterior body rather than "
            "the splenium), or laterally off the midline."
        ),
    },
    "RALTH": {
        "full_name": "Right Anterolateral Temporal Horn",
        "description": (
            "The anterolateral tip of the right temporal horn of the "
            "lateral ventricle."
        ),
        "key_features": (
            "On axial or coronal: follow the temporal horn anteriorly "
            "until it terminates. Place at the most anterior and lateral "
            "extent of the CSF-filled horn."
        ),
        "common_mistakes": (
            "Placing within the horn rather than at its tip, or "
            "confusing the choroid fissure with the horn lumen."
        ),
    },
    "LALTH": {
        "full_name": "Left Anterolateral Temporal Horn",
        "description": (
            "The anterolateral tip of the left temporal horn of the "
            "lateral ventricle."
        ),
        "key_features": (
            "Mirror of RALTH. Axial or coronal: most anterior and "
            "lateral extent of the left temporal horn CSF space."
        ),
        "common_mistakes": (
            "Placing within the horn body rather than at its anterior "
            "tip. Check bilateral symmetry with RALTH."
        ),
    },
    "RSAMTH": {
        "full_name": "Right Superior Anteromedial Temporal Horn",
        "description": (
            "The superior anteromedial extent of the right temporal horn, "
            "near the amygdala."
        ),
        "key_features": (
            "On coronal anterior to the hippocampal head: find the "
            "superomedial corner of the temporal horn where it abuts "
            "the amygdala. This is a tight, CSF-filled angle."
        ),
        "common_mistakes": (
            "Placing too laterally (on the anterolateral horn) or "
            "confusing with RIAMTH below. RSAMTH is the superior corner."
        ),
    },
    "LSAMTH": {
        "full_name": "Left Superior Anteromedial Temporal Horn",
        "description": (
            "The superior anteromedial extent of the left temporal horn, "
            "near the amygdala."
        ),
        "key_features": (
            "Mirror of RSAMTH. Coronal anterior to hippocampal head: "
            "superomedial corner of the left temporal horn."
        ),
        "common_mistakes": (
            "Confusing with LIAMTH (inferior corner) or LALTH (lateral). "
            "Check bilateral symmetry."
        ),
    },
    "RIAMTH": {
        "full_name": "Right Inferior Anteromedial Temporal Horn",
        "description": (
            "The inferior anteromedial extent of the right temporal horn, "
            "near the hippocampal head."
        ),
        "key_features": (
            "On coronal at the hippocampal head: the inferomedial corner "
            "of the right temporal horn where the horn curves around the "
            "hippocampus. Inferior to RSAMTH in the same coronal plane."
        ),
        "common_mistakes": (
            "Placing on the hippocampal surface rather than in the "
            "CSF-filled corner of the horn, or confusing with RSAMTH "
            "(which is superior)."
        ),
    },
    "LIAMTH": {
        "full_name": "Left Inferior Anteromedial Temporal Horn",
        "description": (
            "The inferior anteromedial extent of the left temporal horn, "
            "near the hippocampal head."
        ),
        "key_features": (
            "Mirror of RIAMTH. Coronal at hippocampal head: inferomedial "
            "corner of the left temporal horn."
        ),
        "common_mistakes": (
            "Confusing with LSAMTH (superior corner). Verify by "
            "checking RIAMTH for bilateral symmetry."
        ),
    },
    "RIGO": {
        "full_name": "Right Indusium Griseum Origin",
        "description": (
            "The origin of the right indusium griseum — a thin grey "
            "matter strip on the superior surface of the corpus callosum "
            "continuous with the dentate gyrus."
        ),
        "key_features": (
            "On sagittal: trace the superior surface of the genu of the "
            "CC posteriorly. The RIGO is at the point where the indusium "
            "griseum first appears on the right side, just posterior to "
            "the genu on the CC surface."
        ),
        "common_mistakes": (
            "Placing on the CC body surface rather than at the origin "
            "point, or confusing with the cingulate gyrus above."
        ),
    },
    "LIGO": {
        "full_name": "Left Indusium Griseum Origin",
        "description": (
            "The origin of the left indusium griseum on the superior "
            "surface of the corpus callosum."
        ),
        "key_features": (
            "Mirror of RIGO. Sagittal: posterior to the genu on the "
            "left surface of the CC where the indusium griseum begins."
        ),
        "common_mistakes": (
            "Same as RIGO — avoid placing on the cingulate gyrus or "
            "mid-body of the CC."
        ),
    },
    "RVOH": {
        "full_name": "Right Ventral Occipital Horn",
        "description": (
            "The most ventral and posterior tip of the right occipital "
            "horn of the lateral ventricle."
        ),
        "key_features": (
            "On axial: follow the occipital horn posteriorly to its "
            "terminal point. Place at the most posterior–inferior "
            "tip of the right CSF-filled horn."
        ),
        "common_mistakes": (
            "Placing mid-horn rather than at the terminal tip, or "
            "including the calcar avis (the white matter bulge into "
            "the occipital horn) as part of the CSF space."
        ),
    },
    "LVOH": {
        "full_name": "Left Ventral Occipital Horn",
        "description": (
            "The most ventral and posterior tip of the left occipital "
            "horn of the lateral ventricle."
        ),
        "key_features": (
            "Mirror of RVOH. Axial: most posterior–inferior tip of the "
            "left occipital horn."
        ),
        "common_mistakes": (
            "Same as RVOH. Check bilateral symmetry with RVOH."
        ),
    },
    "ROSF": {
        "full_name": "Right Olfactory Sulcal Fundus",
        "description": (
            "The deepest point of the right olfactory sulcus on the "
            "orbital (inferior) surface of the right frontal lobe."
        ),
        "key_features": (
            "On coronal through the frontal lobe: the olfactory sulcus "
            "is a vertical groove on the orbital surface housing the "
            "olfactory tract. Place at the deepest point (fundus) of "
            "this sulcus on the right side."
        ),
        "common_mistakes": (
            "Placing on the olfactory tract itself rather than the "
            "sulcal fundus, or confusing with the medial orbital sulcus."
        ),
    },
    "LOSF": {
        "full_name": "Left Olfactory Sulcal Fundus",
        "description": (
            "The deepest point of the left olfactory sulcus on the "
            "orbital surface of the left frontal lobe."
        ),
        "key_features": (
            "Mirror of ROSF. Coronal: deepest point of the left "
            "olfactory sulcus on the orbital frontal surface."
        ),
        "common_mistakes": (
            "Same as ROSF — check bilateral symmetry and use the "
            "olfactory tract as a guide to find the sulcus."
        ),
    },
}
