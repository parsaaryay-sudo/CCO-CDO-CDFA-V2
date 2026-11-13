"""Educational text. Everything here is taken from (or summarised from) the supplied guide:
cco_cdo_cdfa_atc_guide.txt. Section numbers refer to that guide."""

OBJECTIVES = [
    "Define CCO, CDO and CDFA and name the flight phase each one covers.",
    "Explain why step-ups, step-downs and \"dive and drive\" level segments cost fuel, add workload or raise CFIT risk.",
    "List what controllers can do to help: altitude windows, speed control, Distance-to-Go, \"Descend via STAR\" and smooth vectoring.",
    "Describe how CNS tools (CPDLC, PBN, Baro-VNAV, SBAS/LPV, ADS-B) and ATM tools (TBO, AMAN, DMAN) support continuous profiles.",
    "Weigh the SID/STAR crossing trade-off between vertical efficiency, safety, capacity and workload.",
]

SUMMARY_CARDS = [
    ("CCO", "g", "Departure phase, from takeoff to Top of Climb (ToC). The aircraft climbs continuously with optimum climb thrust."),
    ("CDO", "c", "Arrival and descent phase, from Top of Descent (ToD) to the Final Approach Fix (FAF). Engines stay at low thrust or idle."),
    ("CDFA", "a", "Final approach of a Non-Precision Approach (NPA). A constant vertical descent angle replaces dangerous step-downs and prevents CFIT."),
]

MATRIX = [
    ("Primary flight phase", "Takeoff to Top of Climb", "Top of Descent to FAF", "FAF to runway threshold / DDA"),
    ("Primary goal", "Fuel efficiency and climb", "Fuel savings and noise", "Flight safety and CFIT elimination"),
    ("Engine thrust", "Optimum climb thrust", "Minimum / idle thrust", "Stabilized approach thrust"),
    ("Method replaced", "Step-up altitude holds", "Step-down level-offs", "\"Dive and drive\" at MDA"),
    ("ATC facilitation", "Altitude windows on SIDs", "Altitude windows, DTG, AMAN", "Vectoring smoothly prior to FAF"),
    ("Critical reference", "Initial cruise flight level", "Top of Descent (ToD)", "Derived Decision Altitude (DDA)"),
]

PHASES = {
    "CCO": {
        "title": "Continuous Climb Operations (CCO)",
        "tagline": "Keep departures climbing from takeoff toward the initial cruising level.",
        "definition": ("CCO is an aircraft operating technique enabled by integrated airspace design, procedure design and "
                       "tactical ATC clearances. Rather than holding an aircraft at intermediate step-up altitudes during "
                       "departure, CCO lets it climb continuously from takeoff toward its initial cruising flight level "
                       "using optimum climb thrust and speeds."),
        "benefits_title": "Fuel efficiency and environmental impact (guide 1.2)",
        "benefits": [
            "<b>High-fuel flight phase:</b> climb burns fuel at the highest rate of the flight. Level-offs at lower altitudes make engines less efficient per kilometre flown than at cruising altitude.",
            "<b>Eliminating step climbs:</b> avoiding unnecessary level-off segments reduces total fuel burn and CO2 emissions.",
            "<b>Noise mitigation:</b> optimum climb gradients gain altitude faster, moving noise footprints away from populated areas.",
        ],
        "atc_title": "The ATC perspective and airspace design (guide 1.3)",
        "atc": [
            "<b>Workload reduction:</b> continuous climb profiles need fewer R/T clearances and intermediate altitude readbacks for pilots and controllers.",
            "<b>Flexible altitude restrictions:</b> minimise hard altitude constraints on SIDs. A window such as \"at or above 7,000 ft\" is preferable to a rigid \"at 7,000 ft\", so different aircraft types can keep their optimum profiles.",
            "<b>Balancing CCO and CDO:</b> in congested TMAs, departure routes often cross arrival flows. When a trade-off is unavoidable, remember that a level segment during climb burns significantly more fuel than an equivalent level segment during descent.",
        ],
        "takeaways": [
            "CCO is not just a pilot technique; it depends on controller clearances and unrestrictive SID designs.",
            "Proactive airspace management and timely climb clearances preserve fuel efficiency and lower workload.",
            "Balancing arrival and departure profiles in busy airspace requires understanding performance differences between aircraft types.",
        ],
    },
    "CDO": {
        "title": "Continuous Descent Operations (CDO)",
        "tagline": "Keep arrivals descending smoothly at low thrust from Top of Descent.",
        "definition": ("CDO is an aircraft operating technique enabled by appropriate airspace design, procedure design and "
                       "tactical ATC clearances. Instead of traditional step-down approach profiles with several intermediate "
                       "level-offs at lower altitudes, CDO lets arriving aircraft keep a continuously descending vertical "
                       "profile, ideally from Top of Descent (TOD) down to the Final Approach Fix (FAF) or ILS intercept point, "
                       "using minimum engine thrust (idle) and low-drag configurations."),
        "benefits_title": "Operational and environmental benefits (guide 2.2)",
        "benefits": [
            "<b>Fuel and emissions reduction:</b> avoiding level-offs at low altitudes, where jet engines burn significantly more fuel, minimises fuel consumption and CO2.",
            "<b>Noise mitigation:</b> staying higher longer before descending continuously reduces the noise footprint over nearby communities by up to 40% (1 to 5 dB).",
            "<b>Workload and safety:</b> replacing multiple step-down clearances with a continuous path reduces frequency chatter and readback/hearback errors.",
        ],
        "atc_title": "The ATC perspective: facilitation and airspace design (guide 2.3)",
        "atc": [
            "<b>Altitude windows:</b> minimise rigid constraints on STARs. \"At or above 7,000 ft\" lets the FMS compute its optimum glide path.",
            "<b>Speed control vs vectoring:</b> early speed adjustments above 10,000 ft (keeping around 280 kt) are far more effective for CDO than tactical radar vectoring.",
            "<b>Distance-to-Go (DTG):</b> when vectoring is unavoidable, give accurate DTG so the crew and FMS can manage kinetic and potential energy.",
            "<b>Sequencing tools:</b> AMAN and route designs such as Point Merge merge and sequence arrival streams early without sacrificing vertical efficiency.",
        ],
        "takeaways": [
            "Energy management is critical: CDO relies on smooth energy dissipation, and unexpected low-altitude level-offs disrupt it.",
            "Clear, timely clearances such as \"Descend via STAR\" let aircraft comply with lateral profiles and vertical windows while descending continuously.",
            "Capacity versus efficiency: a high percentage of CDOs needs proactive planning, early sequencing and close cooperation between Sector and Arrival controllers.",
        ],
    },
    "CDFA": {
        "title": "Continuous Descent Final Approach (CDFA)",
        "tagline": "Fly non-precision approaches on a constant, stabilized slope.",
        "definition": ("CDFA is a flying technique for the final approach segment of a Non-Precision Approach (NPA). Rather than "
                       "descending in steps, the aircraft keeps a continuous, stabilized descent along a predefined Vertical "
                       "Descent Angle (VDA), typically 3 degrees, from the Final Approach Fix (FAF) to the runway threshold or "
                       "Decision Altitude."),
        "benefits_title": "Dive and drive vs CDFA: the safety paradigm (guide 3.2 and 3.3)",
        "benefits": [
            "<b>The dive-and-drive hazard:</b> pilots descend to the minimum altitude of each segment and fly level at low altitude, sometimes as low as 250 ft above the ground in cloud, until the next fix or the MDA.",
            "<b>Workload and CFIT risk:</b> multiple power, pitch and configuration changes near the ground raise cockpit workload and significantly increase the risk of Controlled Flight Into Terrain.",
            "<b>The CDFA solution:</b> no extended level flight at MDA. The approach becomes \"precision-like\", keeping the aircraft higher longer on a stabilized slope to touchdown.",
            "<b>VDA and DDA:</b> VDA is normally 2.75 to 3.77 degrees (3.0 optimum). Operators add a buffer to the MDA to set a Derived Decision Altitude; at the DDA the pilot lands visually or goes around without dipping below the MDA.",
            "<b>Stabilized approach:</b> stable airspeed, a constant descent rate (typically under 1,000 fpm) and landing configuration before low altitudes.",
        ],
        "atc_title": "The ATC perspective and final approach management (guide 3.4)",
        "atc": [
            "<b>Enhanced predictability:</b> constant groundspeed and descent profile make radar monitoring and spacing more predictable.",
            "<b>Vectoring to final:</b> vector aircraft to intercept the final approach course far enough before the FAF so crews can configure and capture the published VDA smoothly.",
            "<b>Safety enhancement:</b> emphasising CDFA in procedure design and ATC operations supports global safety goals by reducing CFIT on non-precision approaches.",
        ],
        # The guide has no numbered "Key Takeaways" list for CDFA, so these summarise section 3.
        "takeaways": [
            "CDFA replaces level flight at MDA with one continuous slope (VDA, typically 3 degrees).",
            "The decision point is the DDA (MDA plus a buffer), so the aircraft never dips below the published MDA.",
            "Controllers help by vectoring to final early enough for a stabilized, predictable approach.",
        ],
    },
}

CNS_CARDS = [
    ("Communication (C): data link and standardized clearances", [
        "<b>CPDLC and R/T workload reduction:</b> Controller-Pilot Data Link Communications and automated communications decrease frequency chatter and readback/hearback errors when issuing complex vertical profiles.",
        "<b>Standardized phraseology:</b> clear tactical clearances such as \"Descend via STAR\", or explicit speed/altitude constraint cancellations, let pilots and the FMS keep descending continuously while respecting procedure limits.",
    ]),
    ("Navigation (N): PBN, VNAV and advanced route architectures", [
        "<b>Performance-Based Navigation:</b> RNAV and RNP allow closed-path SIDs and STARs with published altitude windows (\"at or above\"), so the FMS can compute precise continuous climb and descent trajectories.",
        "<b>Vertical guidance for CDFA:</b> Baro-VNAV and SBAS/LPV give geometric vertical guidance on non-precision approaches, establishing a constant VDA without ILS ground infrastructure.",
        "<b>Point Merge:</b> standardized PBN route structures let controllers sequence arrivals smoothly while maintaining continuous descent profiles.",
    ]),
    ("Surveillance (S): real-time tracking and tactical support", [
        "<b>High-precision tracking:</b> ADS-B and radar give controllers accurate 3D position and altitude data to monitor vertical profile adherence continuously.",
        "<b>Distance-to-Go delivery:</b> accurate surveillance data enables precise DTG updates during radar vectoring.",
        "<b>Arrival Management (AMAN):</b> automated tools process surveillance data to sequence arrivals early, in cruise or at top of descent.",
    ]),
    ("ATM: Trajectory-Based Operations (TBO)", [
        "Integrated ATM moves control toward TBO, where en-route, terminal (APP) and tower (TWR) controllers collaborate with operators to facilitate uninterrupted continuous climb and descent trajectories across multiple sectors.",
    ]),
    ("ATM: AMAN / DMAN and cross-sector coordination", [
        "<b>AMAN / DMAN integration:</b> they process real-time surveillance data to sequence arriving and departing aircraft early. Setting the arrival sequence while aircraft are at cruising altitude allows early speed adjustments instead of low-altitude level-offs.",
        "<b>Cross-sector coordination:</b> standardized hand-offs between En-Route ACC and Approach Control (APP) avoid forcing aircraft to level off when passing between sectors.",
    ]),
]

BENEFITS_BLOCK = {
    "Environmental (guide 7.1)": [
        "Intermediate level-offs force engines to run at high thrust at lower, denser altitudes; continuous operations eliminate these segments.",
        "EUROCONTROL studies indicate annual network savings of up to 340,000 tonnes of fuel and 1.1 million tonnes of CO2.",
        "Keeping arrivals higher longer at idle thrust reduces noise footprints by up to 40% (1 to 5 dB).",
    ],
    "Economic and safety (guide 7.2)": [
        "Non-CDO flights lose an average of 217 seconds in low-altitude level flight, wasting 46 kg of extra fuel per arrival.",
        "CDFA converts non-precision approaches into precision-like profiles, removing terrain-collision risk from low-altitude level flight.",
    ],
}

CHALLENGES = [
    ("Capacity vs vertical efficiency (guide 8.1)",
     ["Controllers must constantly balance vertical flight efficiency against airspace safety, traffic throughput and ATC workload."]),
    ("TMA constraints and traffic conflicts (guide 8.2)", [
        "<b>Departure vs arrival conflicts:</b> in busy TMAs, SID and STAR routes frequently cross. Safe separation between climbing and descending aircraft often requires intermediate level-offs.",
        "<b>Fuel trade-off principle:</b> an aircraft forced into a level segment during climb burns significantly more fuel than an equivalent aircraft holding a level segment during descent.",
        "<b>Fleet heterogeneity:</b> TMAs handle fleets with very different climb/descent capabilities, so use wide altitude windows (\"at or above\") instead of hard constraints.",
    ]),
]

QUIZ = [
    dict(q="Which flight phase does Continuous Climb Operations (CCO) focus on?",
         options=["Top of Descent to the Final Approach Fix", "Takeoff to Top of Climb", "FAF to runway threshold", "Cruise only"],
         answer=1, why="CCO covers the departure phase from takeoff to Top of Climb, using optimum climb thrust."),
    dict(q="How does the guide say an early arrival sequence (AMAN) helps continuous descents?",
         options=["It allows early speed adjustments at cruise altitude instead of low-altitude level-offs",
                  "It replaces the need for any altitude windows",
                  "It lets aircraft ignore STAR lateral profiles",
                  "It allows controllers to stop using speed control"],
         answer=0, why="Establishing the arrival sequence while aircraft are at cruising altitude enables early speed adjustments rather than level-offs at low altitude."),
    dict(q="Which altitude constraint style do the SID/STAR guidance recommend?",
         options=["Hard altitudes such as \"at 7,000 ft\"", "Altitude windows such as \"at or above 7,000 ft\"", "No altitude information at all", "Only altitudes below 3,000 ft"],
         answer=1, why="Windows let the FMS and different aircraft types fly their optimum profiles; hard constraints should be minimised."),
    dict(q="For maintaining CDO profiles, what does the guide say is far more effective than tactical radar vectoring?",
         options=["Holding patterns", "Speed control, especially early adjustments above 10,000 ft (around 280 kt)", "Extra level-offs", "Reducing the number of STARs"],
         answer=1, why="Early speed control keeps the aircraft on an energy-efficient continuous descent; vectoring removes track miles and DTG certainty."),
    dict(q="What is the Vertical Descent Angle (VDA) range and the optimum value given for CDFA?",
         options=["2.0 to 3.0 degrees, optimum 2.5", "2.75 to 3.77 degrees, optimum 3.0", "3.0 to 5.0 degrees, optimum 4.0", "1.5 to 2.5 degrees, optimum 2.0"],
         answer=1, why="The VDA is normally between 2.75 and 3.77 degrees, with 3.0 degrees as optimum."),
    dict(q="Why is the traditional \"dive and drive\" method hazardous?",
         options=["It uses too much idle thrust", "It requires high workload near the ground and raises CFIT risk during low level flight",
                  "It prevents the use of the MDA", "It needs ILS ground equipment"],
         answer=1, why="Multiple power, pitch and configuration changes near the ground raise workload, and level flight at low altitude (sometimes about 250 ft above ground) increases CFIT risk."),
    dict(q="What is the Derived Decision Altitude (DDA)?",
         options=["The FAF altitude plus 1,000 ft", "The MDA plus a small safety buffer, where the pilot decides to land visually or go around",
                  "The altitude at Top of Descent", "The cruise level minus 3,000 ft"],
         answer=1, why="At the DDA the pilot lands visually or immediately executes a missed approach without dipping below the published MDA."),
    dict(q="What descent rate does the guide give as typical for a stabilized approach?",
         options=["Under 1,000 fpm", "Over 2,000 fpm", "Exactly 1,500 fpm", "No limit is mentioned"],
         answer=0, why="A stabilized approach has stable airspeed, a constant descent rate (typically under 1,000 fpm) and landing configuration before low altitudes."),
    dict(q="According to the guide, what do flights flying non-CDO profiles lose on average?",
         options=["60 seconds and 10 kg of fuel", "217 seconds in level flight and 46 kg of extra fuel per arrival", "500 seconds and 200 kg of fuel", "No measurable loss"],
         answer=1, why="Section 7.2: an average of 217 seconds in low-altitude level flight, wasting 46 kg of extra fuel per arrival."),
    dict(q="When a SID and a STAR cross and one aircraft must level off, which statement matches the guide?",
         options=["A level segment in climb burns significantly more fuel than an equivalent one in descent",
                  "A level segment in descent always burns more fuel than one in climb",
                  "Both cost exactly the same fuel", "Level-offs never affect fuel burn"],
         answer=0, why="Section 8.2 (fuel trade-off principle): a forced level segment during climb burns significantly more fuel than an equivalent segment during descent."),
]
