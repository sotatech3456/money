from __future__ import annotations

from pathlib import Path

from modeling.common import write_jsonl


OUTPUT_FILE = Path("modeling/long_form_benchmark.jsonl")


ARTICLE_ROWS: list[dict[str, str]] = [
    {
        "article": "Public Transit",
        "background_circumstance": "In recent years, many large cities have struggled with traffic congestion and rising air pollution.",
        "cause_explanation": "Because private cars occupy road space inefficiently, expanding public transit can reduce both delays and emissions.",
        "example_elaboration": "For example, Seoul and Vienna have shown that reliable rail networks can move large numbers of commuters with less environmental cost.",
        "contrast_concession": "However, critics argue that new transit systems are too expensive for cities already under budget pressure.",
        "evaluation_interpretation": "This objection overlooks the fact that long-term health and productivity gains often outweigh the initial cost.",
        "summary_conclusion": "In conclusion, governments should treat public transportation as a core investment rather than an optional convenience.",
    },
    {
        "article": "Online Learning",
        "background_circumstance": "Today, schools are under pressure to offer flexible learning options for students with different schedules and needs.",
        "cause_explanation": "Because these tools reduce barriers to access, they can improve participation for students who might otherwise fall behind.",
        "example_elaboration": "For instance, recorded lectures and shared discussion boards give students multiple ways to review material at their own pace.",
        "contrast_concession": "Although online instruction cannot replace every classroom experience, it allows more students to stay connected to education during disruptions.",
        "evaluation_interpretation": "This suggests that the value of online learning lies not only in convenience but also in educational equity.",
        "summary_conclusion": "Overall, schools should combine online and in-person teaching instead of treating them as opposites.",
    },
    {
        "article": "School Uniforms",
        "background_circumstance": "Historically, school uniform policies have been introduced as a way to create visible order in educational settings.",
        "cause_explanation": "Supporters say uniforms reduce peer pressure by limiting competition over expensive clothes.",
        "example_elaboration": "For example, when students wear similar outfits, visible status differences can become less immediate in daily interactions.",
        "contrast_concession": "On the other hand, opponents contend that uniforms suppress self-expression and do little to address deeper causes of inequality.",
        "evaluation_interpretation": "That criticism is important because discipline policies should not be confused with real solutions to poverty or exclusion.",
        "summary_conclusion": "Therefore, if schools adopt uniforms, they should do so modestly and without exaggerating what the policy can achieve.",
    },
    {
        "article": "Remote Work",
        "background_circumstance": "After the rapid shift to home offices, many companies are reconsidering what daily work should look like.",
        "cause_explanation": "Remote work can raise productivity because employees lose less time to commuting and interruptions.",
        "example_elaboration": "For example, a software team may reserve office days for planning while completing focused coding tasks from home.",
        "contrast_concession": "Still, some managers argue that remote work weakens mentoring and makes collaboration feel less spontaneous.",
        "evaluation_interpretation": "The real issue is not location itself but whether a team has clear communication habits and measurable goals.",
        "summary_conclusion": "For these reasons, companies should design flexible policies instead of forcing every job into one model.",
    },
    {
        "article": "Renewable Energy",
        "background_circumstance": "Many countries are trying to update power grids while demand for electricity continues to grow.",
        "cause_explanation": "Renewable energy reduces long-term climate risk because it produces power without constantly burning fossil fuels.",
        "example_elaboration": "For instance, offshore wind farms can supply coastal regions while solar panels support daytime household demand.",
        "contrast_concession": "However, renewable sources can be intermittent, and storage technology still requires major investment.",
        "evaluation_interpretation": "This limitation matters, but it shows the need for smarter infrastructure rather than a reason to abandon clean power.",
        "summary_conclusion": "Ultimately, governments should accelerate renewable energy while funding storage, transmission, and backup capacity.",
    },
    {
        "article": "Social Media Age Limits",
        "background_circumstance": "Teenagers now encounter social platforms before many schools have taught digital citizenship in depth.",
        "cause_explanation": "Age limits may protect younger users because they reduce exposure to manipulation, harassment, and addictive design.",
        "example_elaboration": "For example, a platform could require stronger privacy defaults and restricted messaging for users under sixteen.",
        "contrast_concession": "Yet strict bans may also isolate teenagers from communities where they find support and creative opportunities.",
        "evaluation_interpretation": "A simple ban is therefore less meaningful than a policy that changes incentives for platform design.",
        "summary_conclusion": "In summary, age rules should be paired with privacy protections, education, and enforcement against harmful features.",
    },
    {
        "article": "School Lunches",
        "background_circumstance": "In many districts, school meals are one of the few reliable sources of nutrition for low-income students.",
        "cause_explanation": "Free lunches can improve learning because hungry students have more difficulty concentrating in class.",
        "example_elaboration": "For example, breakfast programs often help students arrive ready for exams instead of distracted by hunger.",
        "contrast_concession": "Some taxpayers object that universal programs also support families who could afford to pay.",
        "evaluation_interpretation": "That concern is understandable, but means testing can create stigma and administrative waste.",
        "summary_conclusion": "Therefore, universal school meals are a practical investment in both health and classroom performance.",
    },
    {
        "article": "Urban Green Spaces",
        "background_circumstance": "As cities become denser, residents often have fewer quiet outdoor places near their homes.",
        "cause_explanation": "Parks improve public health because they encourage exercise, reduce heat, and give people space to recover from stress.",
        "example_elaboration": "For instance, tree-lined walking paths can make a neighborhood cooler and more pleasant during summer.",
        "contrast_concession": "However, new parks can raise nearby rents and unintentionally push out the residents they were meant to serve.",
        "evaluation_interpretation": "This risk means green planning must be connected to housing protection, not treated as decoration.",
        "summary_conclusion": "Overall, cities should build green spaces while guarding against displacement.",
    },
    {
        "article": "AI Tutors",
        "background_circumstance": "Students increasingly use chatbots and adaptive software while studying outside the classroom.",
        "cause_explanation": "AI tutors can help because they give immediate practice and explanations when a teacher is not available.",
        "example_elaboration": "For example, a student can ask for another algebra problem after missing a step in the first solution.",
        "contrast_concession": "Nevertheless, automated tutors may give incorrect feedback or encourage students to skip independent thinking.",
        "evaluation_interpretation": "Their value depends on using them as guided practice tools rather than replacements for teachers.",
        "summary_conclusion": "To conclude, schools should allow AI tutoring with transparency, teacher oversight, and clear limits.",
    },
    {
        "article": "Plastic Bag Fees",
        "background_circumstance": "Disposable plastic bags remain common in stores even as communities worry about waste and litter.",
        "cause_explanation": "Small bag fees reduce waste because shoppers are more likely to bring reusable bags when single-use bags cost extra.",
        "example_elaboration": "For instance, grocery stores can display reusable bags near checkout lanes to make the habit easier.",
        "contrast_concession": "Critics argue that the fee can burden low-income shoppers who forget bags or rely on public transportation.",
        "evaluation_interpretation": "That objection shows why environmental policies should be simple, visible, and fair in daily life.",
        "summary_conclusion": "For these reasons, bag fees should remain modest and be paired with free reusable options for vulnerable households.",
    },
    {
        "article": "Four-Day School Week",
        "background_circumstance": "Some rural districts have adopted shorter school weeks to manage transportation costs and teacher shortages.",
        "cause_explanation": "A four-day week may help recruitment because teachers gain more planning time and a better work-life balance.",
        "example_elaboration": "For example, a district might use Fridays for tutoring, professional development, or extracurricular programs.",
        "contrast_concession": "However, families may struggle to find childcare on the weekday when schools are closed.",
        "evaluation_interpretation": "The policy is only fair if communities measure its effect on students whose parents cannot stay home.",
        "summary_conclusion": "In conclusion, districts should test shorter weeks carefully before treating them as a universal reform.",
    },
    {
        "article": "Public Libraries",
        "background_circumstance": "Libraries now serve communities that need internet access, quiet study areas, and trusted local information.",
        "cause_explanation": "Public libraries reduce inequality because they provide free resources that private markets often price out of reach.",
        "example_elaboration": "For example, job seekers can use library computers to write resumes and complete online applications.",
        "contrast_concession": "Some officials claim that digital information makes physical libraries less necessary.",
        "evaluation_interpretation": "That view misses the library's role as a shared civic space, not merely a warehouse for books.",
        "summary_conclusion": "Therefore, cities should modernize libraries instead of cutting them when budgets tighten.",
    },
    {
        "article": "Homework Limits",
        "background_circumstance": "Students often balance school assignments with sports, family responsibilities, and part-time work.",
        "cause_explanation": "Limiting homework can improve well-being because excessive assignments reduce sleep and increase stress.",
        "example_elaboration": "For instance, a teacher might replace nightly worksheets with one focused project and short review exercises.",
        "contrast_concession": "At the same time, some practice outside class is necessary for skills such as writing and mathematics.",
        "evaluation_interpretation": "The question is not whether homework exists, but whether each assignment has a clear learning purpose.",
        "summary_conclusion": "Overall, schools should set homework limits while preserving meaningful practice.",
    },
    {
        "article": "Electric Vehicles",
        "background_circumstance": "Car manufacturers are releasing more electric models as governments set stricter emissions targets.",
        "cause_explanation": "Electric vehicles can lower urban pollution because they do not release exhaust from tailpipes.",
        "example_elaboration": "For example, city buses that run on electricity can reduce diesel fumes along crowded routes.",
        "contrast_concession": "However, batteries require minerals whose mining can damage communities and ecosystems.",
        "evaluation_interpretation": "This tradeoff means clean transportation must include responsible supply chains, not just cleaner streets.",
        "summary_conclusion": "Ultimately, electric vehicles should be expanded alongside recycling, transit, and ethical mineral standards.",
    },
    {
        "article": "Community Gardens",
        "background_circumstance": "Vacant lots in many neighborhoods sit unused while residents lack affordable fresh produce.",
        "cause_explanation": "Community gardens strengthen neighborhoods because residents work together on visible shared projects.",
        "example_elaboration": "For instance, volunteers can grow tomatoes, herbs, and peppers on land that previously attracted trash.",
        "contrast_concession": "Still, gardens require maintenance, water access, and long-term permission to use the land.",
        "evaluation_interpretation": "Their significance is social as much as nutritional because they give neighbors a reason to cooperate.",
        "summary_conclusion": "For these reasons, cities should support gardens with small grants and secure land agreements.",
    },
    {
        "article": "High-Stakes Testing",
        "background_circumstance": "Standardized exams influence school rankings, teacher evaluations, and student placement decisions.",
        "cause_explanation": "High-stakes tests can narrow instruction because teachers feel pressure to focus on tested material.",
        "example_elaboration": "For example, schools may reduce art, science projects, or class discussion to make more room for test drills.",
        "contrast_concession": "Supporters respond that common exams reveal achievement gaps that local grades might hide.",
        "evaluation_interpretation": "That benefit is real, but it becomes harmful when one score is treated as a complete picture of learning.",
        "summary_conclusion": "In summary, tests should inform decisions without dominating the entire school year.",
    },
    {
        "article": "Bike Lanes",
        "background_circumstance": "Many city streets were designed around cars long before cycling became a major commuting option.",
        "cause_explanation": "Protected bike lanes improve safety because they separate cyclists from fast-moving traffic.",
        "example_elaboration": "For instance, concrete barriers and painted intersections can make a busy avenue easier to navigate.",
        "contrast_concession": "Business owners sometimes worry that removing parking spaces will reduce customer visits.",
        "evaluation_interpretation": "That fear should be tested with evidence because safer streets can also increase foot traffic.",
        "summary_conclusion": "Therefore, cities should expand bike lanes while monitoring effects on local businesses.",
    },
    {
        "article": "Minimum Wage",
        "background_circumstance": "Living costs have risen in many regions while wages for service work have grown more slowly.",
        "cause_explanation": "A higher minimum wage can reduce poverty because full-time workers keep more income for rent, food, and transport.",
        "example_elaboration": "For example, a small increase may help a cashier cover bus passes and school supplies without extra shifts.",
        "contrast_concession": "Opponents warn that some small businesses may respond by hiring fewer workers.",
        "evaluation_interpretation": "The policy's fairness depends on balancing worker dignity with support for employers under real pressure.",
        "summary_conclusion": "Overall, wage increases should be gradual, predictable, and paired with help for vulnerable small businesses.",
    },
    {
        "article": "Data Privacy",
        "background_circumstance": "Apps collect location, browsing, and purchase data as ordinary users move through daily life.",
        "cause_explanation": "Stronger privacy rules are needed because users cannot meaningfully negotiate with every service they use.",
        "example_elaboration": "For example, a fitness app may collect health patterns that advertisers or insurers would find valuable.",
        "contrast_concession": "Companies argue that data collection allows them to personalize services and keep products free.",
        "evaluation_interpretation": "Personalization is useful, but it does not justify hiding the real cost of surveillance from users.",
        "summary_conclusion": "In conclusion, privacy law should require clear consent, data limits, and serious penalties for misuse.",
    },
    {
        "article": "Local Journalism",
        "background_circumstance": "Many towns have lost newspapers as advertising revenue moved to large online platforms.",
        "cause_explanation": "Local journalism supports democracy because reporters track school boards, courts, and city budgets.",
        "example_elaboration": "For instance, a local reporter may uncover unsafe housing conditions that national outlets would never notice.",
        "contrast_concession": "Some readers believe social media groups can replace newspapers for community information.",
        "evaluation_interpretation": "That replacement is incomplete because posts rarely provide verification, context, or sustained accountability.",
        "summary_conclusion": "Therefore, communities should experiment with memberships, grants, and public support for local news.",
    },
    {
        "article": "Mental Health Days",
        "background_circumstance": "Schools are seeing more students report anxiety, burnout, and difficulty returning after absences.",
        "cause_explanation": "Mental health days may prevent deeper problems because students can recover before stress becomes a crisis.",
        "example_elaboration": "For example, a student might use an approved absence to attend counseling and complete a catch-up plan.",
        "contrast_concession": "Yet schools must avoid creating a policy that is easy to abuse or that hides chronic attendance problems.",
        "evaluation_interpretation": "The policy is meaningful only if it connects rest with support, not avoidance.",
        "summary_conclusion": "For these reasons, mental health days should be limited, documented, and paired with counseling access.",
    },
    {
        "article": "Public Art",
        "background_circumstance": "Murals, sculptures, and performances often appear in spaces where many people pass each day.",
        "cause_explanation": "Public art can improve civic identity because it gives residents visible symbols of shared history and creativity.",
        "example_elaboration": "For example, a mural near a train station can honor immigrant communities that shaped the neighborhood.",
        "contrast_concession": "However, residents may disagree about which stories deserve public money and public space.",
        "evaluation_interpretation": "That disagreement is productive when it leads to open selection processes rather than closed decisions.",
        "summary_conclusion": "Ultimately, public art should be funded with community participation and transparent criteria.",
    },
    {
        "article": "Water Conservation",
        "background_circumstance": "Drought-prone regions face pressure from population growth, agriculture, and changing rainfall patterns.",
        "cause_explanation": "Conservation rules save water because they reduce waste before reservoirs reach emergency levels.",
        "example_elaboration": "For instance, cities can offer rebates for low-flow fixtures and drought-resistant landscaping.",
        "contrast_concession": "Farmers may argue that strict limits threaten crops and rural livelihoods.",
        "evaluation_interpretation": "That tension shows why water policy must distinguish essential use from avoidable waste.",
        "summary_conclusion": "In summary, conservation should combine household rules, agricultural support, and long-term planning.",
    },
    {
        "article": "Coding Education",
        "background_circumstance": "Many schools are adding programming lessons as digital tools shape more careers.",
        "cause_explanation": "Coding education builds problem-solving skills because students learn to break tasks into smaller steps.",
        "example_elaboration": "For example, beginners can write a simple quiz app that stores questions, checks answers, and shows feedback.",
        "contrast_concession": "However, not every student needs to become a professional software engineer.",
        "evaluation_interpretation": "The broader value is computational thinking, which helps students understand systems even outside technology jobs.",
        "summary_conclusion": "Therefore, coding should be taught as a practical literacy rather than a narrow career track.",
    },
    {
        "article": "Museum Access",
        "background_circumstance": "Museums preserve art, science, and history, but admission fees can exclude many families.",
        "cause_explanation": "Free museum days increase access because cost becomes less of a barrier to cultural learning.",
        "example_elaboration": "For instance, a family might visit a science exhibit on a free weekend and continue learning at home.",
        "contrast_concession": "Museum leaders may worry that free admission reduces revenue needed for staff and preservation.",
        "evaluation_interpretation": "That concern is serious, but public institutions should measure success by reach as well as income.",
        "summary_conclusion": "Overall, museums should offer regular free access while seeking grants and memberships to protect operations.",
    },
]


LABEL_ORDER = (
    "background_circumstance",
    "cause_explanation",
    "example_elaboration",
    "contrast_concession",
    "evaluation_interpretation",
    "summary_conclusion",
)


def main() -> None:
    rows = []
    for article in ARTICLE_ROWS:
        for label in LABEL_ORDER:
            rows.append(
                {
                    "article": article["article"],
                    "text": article[label],
                    "label": label,
                }
            )
    write_jsonl(OUTPUT_FILE, rows)
    print(f"wrote {len(rows)} rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
