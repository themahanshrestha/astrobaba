"""Original text: numerology by life area (used in every section), plus Indian numerology (Mulank, Bhagyank, Namank).
Fields per number: soul (what you need inside), pers (first impression), mind, hobbies, stress, money, friends, growth."""

NUMBER_EXTRA = {
1: dict(soul="freedom to lead and do things your own way", pers="confident, direct and ready to act", mind="you decide fast and say things plainly",
        hobbies="solo challenges, sport and starting new projects", stress="you push harder and get impatient; a hard workout and then a clear plan resets you",
        money="you earn through initiative and take bold risks, so keep a safety buffer", friends="the one who starts plans and takes charge, so leave room for other people's ideas",
        growth="ask for help and listen fully before you decide"),
2: dict(soul="peace, closeness and being truly understood", pers="gentle, tactful and easy to talk to", mind="you listen first and read between the lines",
        hobbies="music, art and quiet shared activities", stress="you absorb tension and avoid conflict; calm company and an honest talk reset you",
        money="you prefer shared, stable money and dislike arguing about it, so agree rules early", friends="the peacemaker who remembers everyone's feelings",
        growth="say what you need out loud, even when it feels uncomfortable"),
3: dict(soul="self-expression and joy shared with others", pers="lively, charming and fun", mind="you think in stories and talk your way to clarity",
        hobbies="writing, performing, social events and creative play", stress="you scatter or turn moody; creating something and seeing friends resets you",
        money="you spend on experiences and can earn from creative work, so track the small spends", friends="the spark who keeps the mood light and connects people",
        growth="finish what you start and share the harder feelings, not only the fun ones"),
4: dict(soul="security, order and something solid you built yourself", pers="dependable, practical and serious", mind="you think step by step and prefer facts to guesses",
        hobbies="building, gardening, crafts and learning a skill slowly", stress="you get rigid and overwork; a routine, a plan and proper rest reset you",
        money="you save steadily and distrust get-rich-quick ideas, but allow some for enjoyment", friends="the reliable one people lean on in a crisis",
        growth="stay flexible when plans change and rest without guilt"),
5: dict(soul="freedom, variety and new experiences", pers="magnetic, adaptable and curious", mind="you think fast, jump between ideas and persuade easily",
        hobbies="travel, meeting new people and trying unusual things", stress="you get restless and impulsive; movement and a change of scene reset you",
        money="money comes and goes with your moods, so automate your saving", friends="the adventurous one who brings new people and ideas",
        growth="commit to one thing long enough to see it through"),
6: dict(soul="love, harmony and a home or community to care for", pers="warm, caring and responsible", mind="you think about how people feel and how to make things better",
        hobbies="cooking, hosting, gardening and family or home projects", stress="you take on too much for others; time just for you resets you",
        money="you spend generously on family and home, so keep a personal savings line", friends="the caregiver who hosts and holds the group together",
        growth="care for others without controlling them, and accept help yourself"),
7: dict(soul="quiet, truth and understanding how things really work", pers="calm, thoughtful and a little mysterious", mind="you analyse deeply and trust evidence over opinion",
        hobbies="reading, research, nature, puzzles and meditation", stress="you withdraw and overthink; solitude in nature and then one honest chat reset you",
        money="you research before spending and prefer simple, lasting choices", friends="the thoughtful friend with a few deep bonds",
        growth="share what you think before it is perfect and let people in"),
8: dict(soul="achievement, respect and real influence", pers="confident, capable and authoritative", mind="you think in goals, results and strategy",
        hobbies="strategy games, fitness goals, investing and building a project", stress="you overwork and try to control things; a hard stop to the day and real rest reset you",
        money="you are strong with money and ambition, so make sure it also funds joy and people", friends="the strong one who gets things done and helps friends succeed",
        growth="measure yourself by more than status and let others lead sometimes"),
9: dict(soul="a chance to make a difference and be part of something bigger", pers="kind, wise and understanding", mind="you see the big picture and think about people and meaning",
        hobbies="volunteering, art, travel and learning about other cultures", stress="you carry the world's problems and struggle to let go; creative time and forgiving yourself reset you",
        money="you give freely and may forget to save, so set automatic limits", friends="the generous friend who helps everyone and forgives easily",
        growth="let go of what is finished and give without needing something back"),
11: dict(soul="meaning, inspiration and a spiritual life", pers="intuitive, sensitive and quietly magnetic", mind="you work by intuition and flashes of insight, then need time to ground them",
         hobbies="art, music, meditation, nature and anything that lifts spirits", stress="your nerves run high and doubt creeps in; quiet, sleep and routine ground you",
         money="your income may follow your inspiration, so keep simple systems for the basics", friends="the sensitive friend people confide in and learn from",
         growth="ground big visions in small daily steps and trust yourself"),
22: dict(soul="something large and lasting that helps many", pers="capable, steady and impressive", mind="you think big and in systems, then plan every step",
         hobbies="building, design, organising projects and mastering a craft", stress="you feel the pressure of your own big goals; breaking tasks into steps and resting reset you",
         money="you can build real wealth through large projects, but guard against overextending", friends="the dependable organiser who makes group plans real",
         growth="start smaller than your vision and allow imperfect progress"),
33: dict(soul="a chance to heal, teach and serve with love", pers="gentle, warm and deeply caring", mind="you think with your heart and explain things with compassion",
         hobbies="teaching, caring for others, creative service and gardening", stress="you give until you are empty; firm boundaries and rest reset you",
         money="you give a lot and may undercharge for your help, so set fair prices", friends="the nurturing friend who sees the best in people",
         growth="keep boundaries so your care lasts, and receive as well as give"),
}

# Indian numerology: each single digit is ruled by a planet
MULANK_PLANET = {1: "Sun", 2: "Moon", 3: "Jupiter", 4: "Rahu", 5: "Mercury", 6: "Venus", 7: "Ketu", 8: "Saturn", 9: "Mars"}
PLANET_THEME = {
    "Sun": "authority, vitality and leadership", "Moon": "feeling, imagination and sensitivity", "Jupiter": "wisdom, optimism and teaching",
    "Rahu": "unconventional thinking, ambition and restlessness", "Mercury": "communication, wit and trade", "Venus": "love, beauty and comfort",
    "Ketu": "detachment, intuition and research", "Saturn": "discipline, patience and hard-won success", "Mars": "energy, courage and drive",
}
INDIAN_INTRO = {
    "mulank": "Your root number, from the day you were born. It shows your basic nature, ruled by {planet}: {theme}.",
    "bhagyank": "Your destiny number, from your whole birth date. It shows the path life tends to lead you along, ruled by {planet}: {theme}.",
    "namank": "Your name number, from your name in the Chaldean system. It colours how the world meets you, ruled by {planet}: {theme}.",
}
RELATION_TEXT = {
    "same": "Your Mulank and Bhagyank are the same number, so your nature and your path point the same way, with extra intensity.",
    "friend": "The planets behind your Mulank and Bhagyank are friendly, so your nature and your path tend to support each other.",
    "enemy": "The planets behind your Mulank and Bhagyank are not natural friends, so your nature and your path can pull in different directions. Treat it as something to work with, not a verdict.",
    "neutral": "The planets behind your Mulank and Bhagyank are neutral to each other: they neither help nor block each other.",
}
