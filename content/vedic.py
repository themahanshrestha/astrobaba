"""Original text for Vedic elements: Nakshatras, Vimshottari dasha, and Sade Sati."""

# name: (traits, gana, animal, text)
NAKSHATRA_INFO = {
"Ashwini": (["initiative", "curiosity"], "Deva", "Horse", "Swift, pioneering and restless; a natural starter with a healing or rescuing streak."),
"Bharani": (["intensity", "discipline"], "Manushya", "Elephant", "Carries heavy responsibility and strong appetites; transformation through endurance."),
"Krittika": (["precision", "radiance"], "Rakshasa", "Sheep", "Sharp, purifying and truthful; cuts through what is false, sometimes too bluntly."),
"Rohini": (["empathy", "steadiness"], "Manushya", "Serpent", "Magnetic, sensual and nurturing; grows beauty and security around itself."),
"Mrigashira": (["curiosity", "exploration"], "Deva", "Serpent", "The gentle seeker; restless curiosity and a lifelong search for something just out of reach."),
"Ardra": (["intensity", "curiosity"], "Manushya", "Dog", "Stormy, intellectual and renewing; clears the old through upheaval, then rebuilds."),
"Punarvasu": (["exploration", "empathy"], "Deva", "Cat", "Optimistic and returning; recovers well, restores hope and finds home again."),
"Pushya": (["empathy", "discipline"], "Deva", "Sheep", "Nourishing, dutiful and supportive; considered the most auspicious nakshatra for care and growth."),
"Ashlesha": (["intensity", "introspection"], "Rakshasa", "Cat", "Perceptive, strategic and magnetic; reads hidden motives and guards itself carefully."),
"Magha": (["radiance", "discipline"], "Rakshasa", "Rat", "Regal and tradition-minded; sense of lineage, dignity and responsibility to lead."),
"Purva Phalguni": (["radiance", "harmony"], "Manushya", "Rat", "Warm, creative and pleasure-loving; makes rest, play and affection a priority."),
"Uttara Phalguni": (["steadiness", "harmony"], "Manushya", "Cow", "Generous and dependable; builds lasting partnerships and helps others."),
"Hasta": (["precision", "curiosity"], "Deva", "Buffalo", "Skilful, witty and resourceful; good with the hands and with practical problem-solving."),
"Chitra": (["precision", "radiance"], "Rakshasa", "Tiger", "Artistic and design-minded; wants to craft something beautiful and distinctive."),
"Swati": (["originality", "harmony"], "Deva", "Buffalo", "Independent and adaptable like a plant swaying in wind; diplomatic and self-reliant."),
"Vishakha": (["initiative", "discipline"], "Rakshasa", "Tiger", "Single-minded and goal-driven; persists until the target is reached."),
"Anuradha": (["harmony", "discipline"], "Deva", "Deer", "Devoted, organised and friendship-oriented; succeeds through cooperation and loyalty."),
"Jyeshtha": (["intensity", "discipline"], "Rakshasa", "Deer", "Protective, senior and sharp-minded; carries responsibility and a strong sense of rank."),
"Mula": (["introspection", "intensity"], "Rakshasa", "Dog", "Root-seeking; wants the truth at the foundation and will uproot what is false."),
"Purva Ashadha": (["exploration", "radiance"], "Manushya", "Monkey", "Invincible optimism and persuasive energy; renews itself and inspires others."),
"Uttara Ashadha": (["discipline", "steadiness"], "Manushya", "Mongoose", "Principled and enduring; slow, lasting success through integrity."),
"Shravana": (["curiosity", "harmony"], "Deva", "Monkey", "Listener and learner; draws wisdom through hearing, connecting and passing on knowledge."),
"Dhanishta": (["discipline", "initiative"], "Rakshasa", "Lion", "Rhythmic, ambitious and resourceful; tends to build wealth and perform well in groups."),
"Shatabhisha": (["introspection", "originality"], "Rakshasa", "Horse", "The hundred healers; private, independent and drawn to unconventional knowledge."),
"Purva Bhadrapada": (["intensity", "originality"], "Manushya", "Lion", "Fiery idealist; transformative and intense, with a strong reformer's streak."),
"Uttara Bhadrapada": (["introspection", "empathy"], "Manushya", "Cow", "Deep, calm and compassionate; carries wisdom and steady spiritual depth."),
"Revati": (["imagination", "empathy"], "Deva", "Elephant", "Gentle guide and traveller; compassionate, imaginative and protective of those on the way."),
}

MAHA_TEXT = {
"Sun": "A period (6 years) that sharpens identity, authority and purpose. Questions of confidence, recognition, and your relationship with leaders and fathers come forward.",
"Moon": "A period (10 years) tuned to emotion, home, family and the public. Mood, sensitivity and sense of belonging are central; nurture routines and close ties.",
"Mars": "A period (7 years) of energy, action and ambition. Drive, competition and courage rise; channel the intensity into work and exercise, and mind your temper.",
"Rahu": "A period (18 years) of hunger, ambition and unconventional paths. Growth often comes through new environments, technology or foreign influences; stay grounded in values.",
"Jupiter": "A period (16 years) of expansion, learning and meaning. Education, teaching, mentors, family growth and opportunity are emphasised; avoid overconfidence.",
"Saturn": "A period (19 years) of structure, responsibility and slow mastery. Effort, patience and facing reality are rewarded; it favours long-term building over shortcuts.",
"Mercury": "A period (17 years) of learning, communication and commerce. Skills, trade, writing, networks and adaptability come forward.",
"Ketu": "A period (7 years) of detachment, simplification and inner search. Letting go, spiritual interest and unusual insight are emphasised; clarify what truly matters.",
"Venus": "A period (20 years) of relationships, creativity and comfort. Love, aesthetics, partnership and prosperity are emphasised; guard against indulgence.",
}

ANTAR_FLAVOR = {
"Sun": "a sub-period focused on identity and recognition",
"Moon": "a sub-period focused on emotion and home",
"Mars": "a sub-period focused on action and effort",
"Rahu": "a sub-period of restlessness and ambition",
"Jupiter": "a sub-period of growth and guidance",
"Saturn": "a sub-period of discipline and responsibility",
"Mercury": "a sub-period of learning and communication",
"Ketu": "a sub-period of release and reflection",
"Venus": "a sub-period of relationships and enjoyment",
}

SADE_SATI = {
"rising": "Saturn is in the sign before your Moon sign (first phase of Saturn's roughly seven-and-a-half-year 'Sade Sati'). Traditionally a season of tightening priorities; practical pressure can ask you to simplify and take responsibility.",
"peak": "Saturn is crossing your Moon sign (the central phase of 'Sade Sati'). Traditionally a season of emotional maturing: heavier responsibilities, and a push to build real inner stability.",
"setting": "Saturn is in the sign after your Moon sign (the final phase of 'Sade Sati'). Traditionally a season of consolidation: lessons settle, and rebuilding becomes easier.",
}

YOGAS = {
"Gaja Kesari": "Jupiter in a kendra (1st, 4th, 7th or 10th) from the Moon: traditionally linked with wisdom, good reputation and resilience.",
"Budha-Aditya": "Sun and Mercury in the same sign: traditionally linked with sharp intellect and communication.",
"Chandra-Mangala": "Moon and Mars together: traditionally linked with enterprise, drive and earning ability, with emotional intensity.",
"Ruchaka": "Mars strong in a kendra: courage, leadership and physical vitality.",
"Bhadra": "Mercury strong in a kendra: eloquence, intellect and business skill.",
"Hamsa": "Jupiter strong in a kendra: wisdom, ethics and a teacher's nature.",
"Malavya": "Venus strong in a kendra: charm, refinement, artistic and relational gifts.",
"Shasha": "Saturn strong in a kendra: discipline, endurance and the capacity to lead structures.",
}
