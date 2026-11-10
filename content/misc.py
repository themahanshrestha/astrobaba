"""Aspect, element and modality text, western house meanings and report scaffolding."""

PAIR_ASPECTS = {
("Sun", "Moon"): {
    "conjunction": "Your Sun and Moon sit together: head and heart pull in the same direction. You are consistent and focused, though you may find it hard to see yourself from outside.",
    "sextile": "Your Sun and Moon cooperate easily: what you want and what you need support one another with a little effort.",
    "square": "Your Sun and Moon form a challenging angle: what you want and what you need pull against each other. It gives drive and inner friction; growth comes from honouring both.",
    "trine": "Your Sun and Moon flow together: a natural inner harmony and ease in being yourself.",
    "opposition": "Your Sun and Moon sit opposite one another (born near a full moon): you feel pulled between needs and goals, and learn balance through relationships and perspective.",
},
("Venus", "Mars"): {
    "conjunction": "Venus and Mars are united in your chart: strong attraction, passion and a direct romantic style; desire and affection run together.",
    "sextile": "Venus and Mars cooperate: affection and desire work together with natural charm.",
    "square": "Venus and Mars are in tension: what you want and how you pursue it can clash, giving passion and some frustration; communicate desire plainly.",
    "trine": "Venus and Mars flow: a natural ease in expressing affection and desire.",
    "opposition": "Venus and Mars oppose: strong chemistry and polarity; you learn to balance giving with asserting.",
},
("Moon", "Saturn"): {
    "conjunction": "Moon and Saturn together: emotional seriousness and self-reliance. You may have learned early to hold feelings in; warmth deepens with trust.",
    "sextile": "Moon and Saturn cooperate: emotional steadiness and a capacity to cope.",
    "square": "Moon and Saturn in tension: a tendency toward self-criticism or emotional restraint. Gentleness with yourself is the work.",
    "trine": "Moon and Saturn flow: calm, mature emotional steadiness.",
    "opposition": "Moon and Saturn oppose: you may feel torn between need for comfort and duty; learn to ask for support.",
},
("Mercury", "Mars"): {
    "conjunction": "Mercury and Mars together: quick, forceful thinking and speech; debate energises you.",
    "sextile": "Mercury and Mars cooperate: decisive, efficient thinking.",
    "square": "Mercury and Mars in tension: sharp words and impatience; slow down before speaking.",
    "trine": "Mercury and Mars flow: clear, courageous communication.",
    "opposition": "Mercury and Mars oppose: arguing and debate come easily; choose your battles.",
},
}

ELEMENT_TEXT = {
"fire": dict(dom="Fire is strong in your chart: enthusiasm, courage and a need to act. Keep an eye on burnout and impatience.",
             low="Fire is light in your chart: you may need to deliberately build confidence and initiative, since they won't always arrive on their own."),
"earth": dict(dom="Earth is strong in your chart: you are practical, reliable and grounded. Watch for stubbornness or an over-focus on the material.",
              low="Earth is light in your chart: grounding routines, body awareness and practical systems will help you make dreams real."),
"air": dict(dom="Air is strong in your chart: you think, talk and connect easily. Watch for overthinking and for living in your head.",
            low="Air is light in your chart: you may need to put feelings into words and seek outside perspective on purpose."),
"water": dict(dom="Water is strong in your chart: you feel deeply and intuit well. Protect your boundaries and your energy.",
              low="Water is light in your chart: you may need to slow down to notice feelings, and practise vulnerability."),
}
MODALITY_TEXT = {
"cardinal": dict(dom="Cardinal energy leads: you initiate and push things forward.", low="Cardinal energy is light: starting things may take deliberate effort."),
"fixed": dict(dom="Fixed energy leads: you persist and resist change.", low="Fixed energy is light: staying with things to the end may take deliberate effort."),
"mutable": dict(dom="Mutable energy leads: you adapt and change easily, and may find focus harder.", low="Mutable energy is light: flexibility may take deliberate effort."),
}

HOUSE_FLAVOR = {
    "career": "Your Midheaven (the public-career point of your chart) is in {sign}",
    "partner": "Your Descendant (the relationship point) is in {sign}",
}

RELATION_TYPES = {
    "romantic": "Romantic partnership",
    "business": "Business partnership",
    "family": "Family bond",
    "friends": "Friendship",
}

DISCLAIMER = ("AstroBaba is for self-reflection and entertainment. Astrology and numerology are traditional symbolic systems, "
              "not scientific predictions, and nothing here is medical, legal, financial or relationship advice. "
              "Use what resonates, question what doesn't, and make your own decisions.")

DIMENSION_TEXT = {
"emotional": dict(
    high="You tend to understand each other's feelings without much effort, and emotional needs mesh well.",
    mid="Your emotional styles differ but can meet in the middle; say what you need rather than expecting to be read.",
    low="You process feelings very differently. Neither is wrong; agree on how you'll handle tension and give each other time to reset."),
"communication": dict(
    high="Conversation flows: you follow each other's thinking and speak a similar language.",
    mid="Communication works with a little translation; clarify assumptions and check understanding.",
    low="Your thinking styles clash easily. Slow down, ask what was meant, and put important things in writing."),
"values": dict(
    high="You value similar things in affection and enjoyment, so giving and receiving feel natural.",
    mid="Your tastes and values differ in places; curiosity about each other's priorities goes a long way.",
    low="What each of you values and finds enjoyable differs notably. Respect the difference, and agree on shared essentials."),
"drive": dict(
    high="Your energies and motivations spark each other and you work well when doing things together.",
    mid="Your pace and drive sometimes differ, so agree on how you decide and divide effort.",
    low="Your drives pull in different directions and can create friction or competition. Define roles and take turns leading."),
"stability": dict(
    high="There is a solid base for lasting trust and shared commitments.",
    mid="Long-term fit is workable, but needs clear commitments and reliable habits.",
    low="Building long-term stability will take deliberate effort: clear agreements, honest check-ins and patience."),
}
DIMENSION_TITLE = {"emotional": "Emotional rapport", "communication": "Communication", "values": "Values & affection",
                   "drive": "Drive & energy", "stability": "Long-term stability"}

RELATION_TIPS = {
"romantic": ["Say what you need directly rather than hoping it is guessed.",
             "Schedule regular, unhurried time together without distractions.",
             "When you disagree, begin with what you appreciate, then name the issue."],
"business": ["Put roles, decision rights and money rules in writing at the start.",
             "Divide work by strengths: let each of you lead where your profile is strongest.",
             "Agree how disagreements are resolved before they happen."],
"family": ["Accept that each of you processes feelings differently and don't take it personally.",
           "Keep a few shared rituals, such as meals or calls, to maintain closeness.",
           "Separate old roles from who you each are now."],
"friends": ["Make time for shared activities, not only conversation.",
            "Be upfront when you need space so it isn't read as distance.",
            "Celebrate each other's wins openly."],
}
