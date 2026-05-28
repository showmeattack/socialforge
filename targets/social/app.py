"""Social Media Simulator — LinkHub (fake LinkedIn) with rich profiles for OSINT."""
import json
import hashlib
import urllib.parse
import httpx
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SocialForge Social")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class AllowIframeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = "default-src * 'unsafe-inline' 'unsafe-eval' data: blob:; frame-ancestors *"
        # CSP already set
        return response


app.add_middleware(AllowIframeMiddleware)

LABS_DIR = Path(__file__).parent.parent.parent / "labs"
NPC_PHOTOS_DIR = Path(r"C:\Users\fargo\Desktop\НПС")

NPC_PHOTO_URLS = {
    # human_chain
    "Ben Morgan":              "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=200&q=80",
    "Rachel Park":             "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=200&q=80",
    "James Cole":              "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&q=80",
    "Sarah Whitfield":         "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=200&q=80",
    "Alex Reed":               "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&q=80",
    # mgm_breach
    "Elena Rodriguez":         "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=200&q=80",
    "Marcus Chen":             "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&q=80",
    "Sarah Mitchell":          "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&q=80",
    # mini_quid_pro_quo
    "Sandra Williams":         "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=200&q=80",
    # mini_authority
    "Priya Sharma":            "https://images.unsplash.com/photo-1524250502761-1ac6f2e30d43?w=200&q=80",
    # mini_smishing
    "David Liu":               "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=200&q=80",
    "Tina Zhao":               "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=200&q=80",
}


@app.get("/photos/{filename:path}")
async def serve_photo(filename: str):
    from fastapi.responses import Response, RedirectResponse
    name = urllib.parse.unquote(filename)
    stem = Path(name).stem if "." in name else name
    # Local files take priority over Unsplash fallbacks
    path = NPC_PHOTOS_DIR / name
    if path.exists():
        return FileResponse(str(path), media_type="image/png")
    path2 = NPC_PHOTOS_DIR / f"{stem}.png"
    if path2.exists():
        return FileResponse(str(path2), media_type="image/png")
    if stem in NPC_PHOTO_URLS:
        return RedirectResponse(url=NPC_PHOTO_URLS[stem], status_code=302)
    stem = Path(name).stem if "." in name else name
    h1 = int(hashlib.md5(stem.encode()).hexdigest()[:6], 16) % 360
    h2 = (h1 + 40) % 360
    initials = "".join(p[0].upper() for p in stem.split() if p)[:2]
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
  <defs>
    <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:hsl({h1},60%,50%)"/>
      <stop offset="100%" style="stop-color:hsl({h2},50%,38%)"/>
    </linearGradient>
    <clipPath id="c"><circle cx="100" cy="100" r="100"/></clipPath>
  </defs>
  <circle cx="100" cy="100" r="100" fill="url(#g)"/>
  <circle cx="100" cy="82" r="34" fill="rgba(255,255,255,0.25)"/>
  <ellipse cx="100" cy="155" rx="52" ry="38" fill="rgba(255,255,255,0.25)"/>
  <text x="100" y="108" text-anchor="middle" font-family="-apple-system,sans-serif" font-size="52" font-weight="700" fill="white" opacity="0.9">{initials}</text>
</svg>"""
    return Response(content=svg, media_type="image/svg+xml")


# ===================== GENERATED POSTS PER PERSONA =====================
# At least 10 posts per persona with OSINT-relevant details

PERSONA_POSTS = {
    # === MGM Breach ===
    "elena_helpdesk": [
        {"text": "Another busy week at the IT Help Desk! Resolved 47 tickets this week alone. Password resets, MFA issues, VPN configs — you name it, we fix it! 💻 #ITSupport #HelpDesk", "date": "April 10, 2024", "likes": 12, "image_url": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=800&q=80"},
        {"text": "Reminder to all Golden Mirage employees: if you need IT assistance, please submit a ticket through ServiceNow. Walk-ins are welcome but tickets help us track and prioritize! #GoldenMirage", "date": "April 5, 2024", "likes": 8},
        {"text": "Proud to have been promoted to Help Desk Lead! 4 years at Golden Mirage and still loving every day. Thank you David Park for believing in me 🙏 #Career #ITCareer", "date": "March 20, 2024", "likes": 45, "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80"},
        {"text": "Just completed our quarterly phishing simulation. 87% of employees correctly identified the test email! We're getting better! 📊 #SecurityAwareness", "date": "March 15, 2024", "likes": 23},
        {"text": "Onboarded 5 new employees today including Marcus Chen in marketing. Welcome to the team! Remember: your temporary password must be changed within 24 hours! 🔐", "date": "April 1, 2024", "likes": 15},
        {"text": "Coffee + ServiceNow dashboard = my Monday morning ritual ☕ Currently at 12 open tickets. Let's get that to zero! #Productivity", "date": "March 25, 2024", "likes": 9},
        {"text": "Had an amazing team dinner with the IT department last night. Shoutout to David Park for organizing! Best boss ever 🎉 #TeamIT #GoldenMirage", "date": "March 10, 2024", "likes": 31, "image_url": "https://images.unsplash.com/photo-1482049016688-2d3e1b311543?w=800&q=80"},
        {"text": "PSA: We're rolling out new MFA tokens next month. ALL employees will need to re-enroll. I'll be sending instructions via ServiceNow. Please don't call the help desk about this — just wait for the email! 😅", "date": "February 28, 2024", "likes": 17},
        {"text": "4 years ago today I walked into Golden Mirage for my first day. From junior tech to Help Desk Lead — hard work pays off! 🎂 #WorkAnniversary #Grateful", "date": "February 15, 2024", "likes": 52},
        {"text": "Attending the ServiceNow Knowledge Conference in Las Vegas next month! Who else is going? Would love to connect! #ServiceNow #ITSM #Know24", "date": "February 1, 2024", "likes": 14, "image_url": "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?w=800&q=80"},
        {"text": "Weekend project: Set up a home lab with Active Directory, SCCM, and Intune. The best way to learn is by doing! 🏠🖥️ #HomeLab #SysAdmin", "date": "January 20, 2024", "likes": 26},
    ],
    "marcus_linkedin": [
        {"text": "First day at Golden Mirage! So grateful to my manager Sarah Mitchell for this opportunity! The onboarding was great — got my badge and everything set up through ServiceNow. #NewJob #Vegas #GoldenMirage", "date": "April 1, 2024", "likes": 89, "badge_photo": True, "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80"},
        {"text": "Two weeks in and already loving the team! The IT onboarding was smooth, shoutout to the ServiceNow ticketing system for making it easy 😂 Already submitted 3 tickets for monitor issues lol", "date": "April 14, 2024", "likes": 34},
        {"text": "Birthday weekend coming up! March 15th is going to be EPIC 🎂🎉 #Pisces #BirthdayBoy", "date": "March 10, 2024", "likes": 67},
        {"text": "Missing mom's cooking in Boston. Nothing beats her clam chowder! 617 forever 💙 #BostonStrong", "date": "March 5, 2024", "likes": 42},
        {"text": "Just crushed a PR at FitLife Gym! 225lb bench press 💪 Who says marketing people can't lift? #GymLife", "date": "February 28, 2024", "likes": 55, "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800&q=80"},
        {"text": "Excited to announce I've accepted a position at Golden Mirage Resort & Casino in Las Vegas! Boston → Vegas! Huge thanks to BU Career Services and everyone who supported me. New chapter starts April 1st! 🎰✨", "date": "March 18, 2024", "likes": 156},
        {"text": "Last day at Boston Harbor Hotels. Grateful for the internship experience — learned so much about hospitality marketing. Onto bigger things! 🌊➡️🎰", "date": "March 28, 2024", "likes": 73},
        {"text": "Biscuit is NOT happy about the move to Vegas 🐕😤 Don't worry buddy, the new apartment has a yard! #DogDad #MovingDay", "date": "March 30, 2024", "likes": 91, "image_url": "https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=800&q=80"},
        {"text": "Spent the weekend exploring the Strip. Found an amazing ramen place off Fremont Street. Vegas is growing on me! 🍜 #VegasLife", "date": "April 7, 2024", "likes": 28, "image_url": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800&q=80"},
        {"text": "Throwback to my BU graduation! Can't believe it's been almost a year. Communications degree putting in WORK 🎓 #BostonUniversity #TBT", "date": "February 15, 2024", "likes": 64},
        {"text": "Pro tip: when your IT help desk asks you to submit a ticket, just submit the ticket. Don't email them directly. Trust me, I learned this the hard way 😂 Elena Rodriguez was very patient though lol #NewEmployee", "date": "April 8, 2024", "likes": 19},
        {"text": "Sunday brunch with the marketing team! Already feels like family 💛 Sarah Mitchell really knows how to build a team culture. #WorkCulture #GoldenMirage", "date": "April 14, 2024", "likes": 37},
    ],
    "sarah_manager": [
        {"text": "Thrilled to welcome Marcus Chen to our marketing team at Golden Mirage! His energy and fresh perspective from Boston University will be a great addition. Welcome aboard, Marcus! 🎰", "date": "April 1, 2024", "likes": 42},
        {"text": "Just wrapped up our Q1 marketing review. Revenue from digital campaigns up 23% YoY. Proud of this incredible team! 📈 #MarketingResults #GoldenMirage", "date": "April 3, 2024", "likes": 67},
        {"text": "Keynote speaker at the Las Vegas Hospitality Marketing Summit next week. Topic: 'Data-Driven Guest Engagement in the Age of AI.' Nervous but excited! 🎤", "date": "March 25, 2024", "likes": 89, "image_url": "https://images.unsplash.com/photo-1537511446984-935f663eb1f4?w=800&q=80"},
        {"text": "15 years in luxury hospitality marketing. Started as a coordinator at The Venetian, now Marketing Director at Golden Mirage. The journey has been incredible. #CareerReflection", "date": "March 15, 2024", "likes": 134, "image_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=800&q=80"},
        {"text": "Hiring alert! We're looking for a Marketing Coordinator to join our team at Golden Mirage. If you love luxury branding and data analytics, reach out! 📩 #Hiring #MarketingJobs", "date": "March 8, 2024", "likes": 56},
        {"text": "Our new loyalty program campaign 'Mirage Gold Rewards' hit 50,000 signups in the first month! When creative meets data, magic happens ✨", "date": "February 20, 2024", "likes": 78, "image_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80"},
        {"text": "Great dinner with our CEO Richard Blackwell discussing 2024 brand strategy. Exciting things ahead for Golden Mirage! Can't share details yet but stay tuned 👀", "date": "February 10, 2024", "likes": 45},
        {"text": "Team building day at Top Golf! Nothing brings a marketing team together like friendly competition 🏌️ Even Marcus hit a hole-in-one (beginner's luck 😂)", "date": "April 12, 2024", "likes": 53, "image_url": "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=800&q=80"},
        {"text": "Attended an amazing cybersecurity awareness session by Lisa Nakamura. Everyone in marketing needs to understand phishing threats — we handle customer data daily! 🔒", "date": "January 30, 2024", "likes": 31},
        {"text": "Celebrating 5 years at Golden Mirage this month! From building the digital team from scratch to managing 12 incredible marketers. Grateful for this journey 🎉", "date": "January 15, 2024", "likes": 112},
    ],

    # === Mini Pretexting — TechStart Inc. ===
    "mike_helpdesk": [
        {"text": "Day 1 at TechStart Inc! Excited to be the go-to IT guy for this awesome startup. 42 employees, 1 helpdesk tech — challenge accepted! 💪 #ITSupport #StartupLife", "date": "January 15, 2024", "likes": 23, "image_url": "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=800&q=80"},
        {"text": "Pro tip for my TechStart colleagues: PLEASE don't tape your password to your monitor. I've found 3 this week alone 🤦 #SecurityBasics", "date": "February 5, 2024", "likes": 45},
        {"text": "Completed the Slack → Teams migration over the weekend. Sorry for any confusion — shoot me a ticket if you're having issues! #ITMigration #TechStart", "date": "February 20, 2024", "likes": 12},
        {"text": "Our CEO Jake Morrison just approved budget for new security tools! Finally getting a proper endpoint protection suite. #CyberSecurity #StartupIT", "date": "March 1, 2024", "likes": 18},
        {"text": "Reminder: we're doing a fire drill AND a cybersecurity drill next Tuesday. Yes, both on the same day. No, I didn't plan it that way 😅 #OfficeLife", "date": "March 10, 2024", "likes": 34},
        {"text": "Weekend warrior mode: studying for my CompTIA Security+ cert. Any study tips? 📚 #Certification #InfoSec", "date": "March 15, 2024", "likes": 27, "image_url": "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=800&q=80"},
        {"text": "Helped onboard 3 new devs today. Tip: when IT asks you to create a complex password, 'password123' is NOT what we mean. True story. 🤣", "date": "March 25, 2024", "likes": 56},
        {"text": "Big shoutout to our Office Manager for keeping the printer alive. That thing has been through wars. 🖨️ #OfficeHero", "date": "April 2, 2024", "likes": 15, "image_url": "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=800&q=80"},
        {"text": "Just set up our new VPN for remote workers. If you're working from home, ping me for your config. Extension 2001 or mike.torres@techstart.io 📞", "date": "April 5, 2024", "likes": 9},
        {"text": "Friday fun fact: This week I resolved my 500th IT ticket at TechStart! 🎉 Most common issue? 'I forgot my password.' Classic. #HelpDesk #Milestone", "date": "April 12, 2024", "likes": 41, "image_url": "https://images.unsplash.com/photo-1517649153209-da8e0c3c20f8?w=800&q=80"},
        {"text": "Loving the startup energy but sometimes I miss the structure of my old corporate gig at Cisco. Then I remember the bureaucracy and I'm grateful 😂 #StartupVsCorporate", "date": "January 28, 2024", "likes": 33},
    ],

    # === Mini Tailgating — SecureVault Financial ===
    "tom_employee": [
        {"text": "3 years at SecureVault Financial! Building the future of secure banking, one commit at a time 🔒💻 #SoftwareDev #Fintech", "date": "March 1, 2024", "likes": 34, "image_url": "https://images.unsplash.com/photo-1517649153209-da8e0c3c20f8?w=800&q=80"},
        {"text": "Our new biometric access system is INTENSE. Fingerprint + badge + PIN just to get into the building. Security level: Fort Knox 🏦 #SecureVault #Security", "date": "February 15, 2024", "likes": 28, "image_url": "https://images.unsplash.com/photo-1554224155-8d04cb24ef21?w=800&q=80"},
        {"text": "Shipped a major update to our fraud detection engine today. Reduced false positives by 40%! The QA team deserves all the credit 🚀 #Fintech #Engineering", "date": "March 20, 2024", "likes": 56},
        {"text": "Working on PCI compliance documentation all week. Not the most exciting work but absolutely critical for our customers' trust. 📋 #PCI #Compliance", "date": "March 25, 2024", "likes": 11},
        {"text": "Weekend hiking in the mountains! Nature is the best debugger 🏔️ Came back with a solution to that race condition bug. #WorkLifeBalance #Hiking", "date": "April 6, 2024", "likes": 42, "image_url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&q=80"},
        {"text": "Just got my AWS Solutions Architect certification! Studied for 3 months but totally worth it. Our CTO Rachel Kim even gave a shoutout in the team meeting 🎓", "date": "February 1, 2024", "likes": 89},
        {"text": "Funny story: a delivery person tried to follow me through the secure door today. I politely told them to check in at reception. Security first, always! 🚪 #PhysicalSecurity", "date": "April 10, 2024", "likes": 18},
        {"text": "Our annual company hackathon is next month! My team is building a real-time transaction anomaly detector using ML. May the best hack win! 🏆 #Hackathon", "date": "March 30, 2024", "likes": 37},
        {"text": "Coffee with our security team lead James Park today. His stories about social engineering attacks are both terrifying and fascinating 😱☕ #InfoSec", "date": "January 25, 2024", "likes": 23},
        {"text": "PSA for my SecureVault colleagues: the parking garage keycard is NOT a replacement for your building access badge. Yes, someone tried this. 😂 #WorkLife", "date": "February 20, 2024", "likes": 45, "image_url": "https://images.unsplash.com/photo-1583416750470-d51bb4edc7b1?w=800&q=80"},
        {"text": "Grateful for a team that does code reviews properly. Caught a potential SQL injection in my PR today — thanks Team! 🙏 #CodeReview #Security", "date": "January 15, 2024", "likes": 31},
    ],

    # === Mini Authority — GreenLeaf Biotech ===
    "priya_analyst": [
        {"text": "Just started my dream job as a Junior Data Analyst at GreenLeaf Biotech! The work we're doing in sustainable agriculture is going to change the world 🌱📊 #NewJob #Biotech", "date": "February 1, 2024", "likes": 67, "image_url": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=800&q=80"},

        {"text": "First week done! My manager Mark Wilson is incredibly knowledgeable. Already learning so much about bioinformatics data pipelines 🧬 #Learning #DataScience", "date": "February 7, 2024", "likes": 34},
        {"text": "Our CEO Robert Chen visited the analytics department today. He's so inspiring — 30 years in biotech and still passionate about every project! 👩‍🔬 #Leadership", "date": "February 20, 2024", "likes": 45, "image_url": "https://images.unsplash.com/photo-1576086213369-f5e53c4e5e4b?w=800&q=80"},
        {"text": "Completed my first solo data analysis report! Analyzed gene expression patterns across 50,000 samples. My statistics degree from NYU is finally paying off 📈 #DataAnalytics", "date": "March 5, 2024", "likes": 52},
        {"text": "Weekend cooking experiment: tried to make dal like my grandmother's recipe. Got close but not quite there yet 🍛 #IndianFood #Cooking", "date": "March 10, 2024", "likes": 38},
        {"text": "Security reminder from IT: always verify unusual requests, even if they appear to come from executives. GreenLeaf takes cybersecurity seriously! 🔐 #SecurityFirst", "date": "March 15, 2024", "likes": 12},
        {"text": "Attended a Python meetup in the city last night. Presented my work on pandas optimization for large genomic datasets. Great feedback! 🐍 #Python #DataScience", "date": "March 22, 2024", "likes": 41},
        {"text": "So proud of GreenLeaf! Our drought-resistant crop strain just passed Phase 2 trials. This could help millions of farmers worldwide 🌾 #Biotech #Innovation", "date": "April 1, 2024", "likes": 78, "image_url": "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=800&q=80"},
        {"text": "Two months at GreenLeaf and I already feel like part of the family. The lab culture here is something special ❤️ #WorkCulture #Grateful", "date": "April 5, 2024", "likes": 29},
        {"text": "Book recommendation: 'The Gene' by Siddhartha Mukherjee. A must-read for anyone in biotech! Currently on my 2nd read 📖 #BiotechReads", "date": "January 28, 2024", "likes": 35},
        {"text": "My NYU professor Dr. Sarah Lee reached out about collaborating on a research paper. Academia meets industry! 🎓🔬 #Research #Collaboration", "date": "April 10, 2024", "likes": 46},
    ],

    # === Mini Smishing — NovaPay ===
    "david_target": [
        {"text": "Finally upgrading my WFH setup — ordered a 4K ultrawide from Amazon. Should be here any day now, can't wait to unbox it! 📦🖥️ #WFHSetup #NewGear", "date": "2 weeks ago", "likes": 47, "image_url": "https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=800&q=80"},
        {"text": "Exciting news: NovaPay just crossed 500K active users! Being Product Manager here is a wild ride 🚀 #Fintech #ProductManagement", "date": "April 1, 2024", "likes": 89, "image_url": "https://images.unsplash.com/photo-1590283603385-17ffb3aa346a?w=800&q=80"},
        {"text": "Launched our new instant transfer feature today! Zero fees for transfers under $500. User feedback has been incredible 💸 #NovaPay #ProductLaunch", "date": "March 15, 2024", "likes": 67},
        {"text": "Weekend road trip with the family! The kids loved the aquarium in San Diego 🐠 Sometimes you need to disconnect from Slack #DadLife #Weekend", "date": "March 23, 2024", "likes": 54},
        {"text": "Sprint retrospective today. Our dev team shipped 34 story points this sprint — new record! 🎯 Huge thanks to the engineering team #Agile #Sprint", "date": "March 28, 2024", "likes": 23},
        {"text": "Just published a blog post on Medium: 'Why User Trust is the #1 Feature in Fintech.' Link in comments 📝 #Fintech #ProductThinking", "date": "February 20, 2024", "likes": 112},
        {"text": "Our CTO Alex Rivera and I just finalized the Q2 product roadmap. Some game-changing features coming to NovaPay. Stay tuned! 👀", "date": "April 5, 2024", "likes": 45},
        {"text": "PSA: Be careful of smishing attacks (SMS phishing)! I've seen some very convincing fake texts pretending to be from payment apps. Always verify through the official app 📱🔐", "date": "February 10, 2024", "likes": 78},
        {"text": "Attended FinTech Connect in San Francisco. Great panels on regulatory compliance and user experience design. Met some amazing founders! 🤝", "date": "January 25, 2024", "likes": 34},
        {"text": "5 years at NovaPay today! From founding team member to Head of Product. What a journey it's been 🎂 #WorkAnniversary #Startup", "date": "January 15, 2024", "likes": 156, "image_url": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&q=80"},
        {"text": "Coaching my son's soccer team this spring ⚽ Turns out managing 8-year-olds is harder than managing product sprints 😂 #CoachDad", "date": "April 8, 2024", "likes": 71},
        {"text": "Mandatory security training complete. NovaPay's security team doesn't mess around — 2-hour session on social engineering tactics. Eye-opening! 🔒", "date": "March 1, 2024", "likes": 16},
    ],
    "tina_zhao": [
        {"text": "NovaPay just crossed 500K active users. This team has earned every single one. Building the future of payments one transaction at a time 💸 #NovaPay #Fintech", "date": "April 1, 2024", "likes": 312, "image_url": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=800&q=80"},
        {"text": "Series C closes in 3 weeks. Can't say the number yet but our lead investor at a16z texted me 'you've earned this.' That text meant everything. 🙏 #VentureCapital #Fintech", "date": "March 22, 2024", "likes": 278},
        {"text": "Regulatory milestone: NovaPay is now licensed in all 50 US states. Three years, one legal team, zero shortcuts. 🇺🇸 #Compliance #Payments #NovaPay", "date": "March 10, 2024", "likes": 445, "image_url": "https://images.unsplash.com/photo-1554224155-8d04cb24ef21?w=800&q=80"},
        {"text": "Morning Peloton, then 3 board calls before noon. That's CEO life on a good week 😅 #ExecutiveLife #Startup", "date": "April 7, 2024", "likes": 67},
        {"text": "Dinner with our CFO and the Goldman team. The revenue story we're telling in 2024 is one I'm proud to tell. Details coming with the Series C announcement. 🍽️", "date": "February 18, 2024", "likes": 134},
        {"text": "Keynote at Money20/20 next week. Topic: Why trust, not features, is the fintech moat. Come say hi! 🎤 #Money2020 #Fintech #Payments", "date": "March 28, 2024", "likes": 98},
        {"text": "Forbes 30 Under 40 in Fintech. I'm 41 so I'll take it 😂 Thank you to the whole NovaPay team — this recognition belongs to everyone. #Forbes #NovaPay", "date": "January 8, 2024", "likes": 567, "image_url": "https://images.unsplash.com/photo-1583416750470-d51bb4edc7b1?w=800&q=80"},
        {"text": "I started NovaPay because I was tired of paying $15 to send money to my parents. Simple problem. Hard solution. Worth every minute. #Founder #WhyWeBuilt", "date": "February 1, 2024", "likes": 389},
        {"text": "Charity gala last night for financial literacy in underserved communities. NovaPay donated $200K. This is the work that matters. ❤️ #FinancialLiteracy #GivingBack", "date": "April 13, 2024", "likes": 203},
        {"text": "Our churn rate for enterprise clients hit an all-time low this quarter. Retention is the metric I care about more than any other. #CustomerSuccess #SaaS #Fintech", "date": "March 5, 2024", "likes": 156},
        {"text": "Flying to NYC tomorrow for investor day. Five meetings, two dinners, one very early flight. Worth every minute of jet lag. ✈️ #InvestorDay #FounderLife", "date": "April 10, 2024", "likes": 87},
    ],
    "kevin_brooks": [
        {"text": "Shipped NovaPay's new transaction routing engine today. P99 latency: 14ms. Previous: 47ms. Four months of work. Worth. Every. PR review. 🚀 #BackendEngineering #Fintech", "date": "April 8, 2024", "likes": 167, "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80"},
        {"text": "Architecture post-mortem: how we migrated 200M transactions to a new schema with zero downtime. Will write this up properly. The key was blue-green with custom rollback gates. 🔧 #SystemDesign", "date": "March 26, 2024", "likes": 234},
        {"text": "Hot take: most 'microservices migrations' are actually monolith-with-HTTP calls. If your services share a database, you have a distributed monolith. Don't @ me. #Architecture #Engineering", "date": "March 15, 2024", "likes": 312, "image_url": "https://images.unsplash.com/photo-1629654291664-a9a13abebdfe?w=800&q=80"},
        {"text": "Talked a junior dev out of rewriting a perfectly fine service in a new framework today. Sometimes the best engineering decision is 'don't.' 😌 #Mentorship #Engineering", "date": "April 3, 2024", "likes": 89},
        {"text": "Prod alert at 02:30 last night. Root cause: an index that got dropped during a migration. Five minute fix, two hours of adrenaline. The on-call life. 🌙 #OnCall #SRE", "date": "February 20, 2024", "likes": 56},
        {"text": "QA team (shoutout to Omar Hassan) found a race condition in the payment reconciliation flow before it hit prod. That's the kind of catch that saves the company. Seriously. Thank you. 🙏", "date": "March 20, 2024", "likes": 78},
        {"text": "Conference recap: StrangeLoop was the best conference I've attended in years. Three talks I'm still thinking about. Strong recommend for anyone who writes distributed systems. 🎓 #StrangeLoop", "date": "October 15, 2023", "likes": 44},
        {"text": "NovaPay is hiring senior backend engineers. TypeScript/Node or Go. Distributed systems experience required. DM me or apply through the site. We move fast. #Hiring #BackendEngineering", "date": "March 1, 2024", "likes": 123, "image_url": "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=800&q=80"},
        {"text": "First rule of production: assume anything can fail. Second rule: design for it anyway. Third rule: still be surprised when it does. Welcome to engineering. 😂 #SoftwareEngineering", "date": "January 18, 2024", "likes": 198},
        {"text": "Reviewing a PR that's 4,000 lines of diff. Whoever approved the scope of this ticket owes me coffee. ☕ #CodeReview #Engineering #TechDebt", "date": "April 12, 2024", "likes": 67},
        {"text": "Resisted the urge to become an engineering manager again this quarter. The craft is still too good. Maybe next year. Maybe never. 🔧 #ICPath #Engineering", "date": "February 10, 2024", "likes": 143},
    ],
    "sarah_lee": [
        {"text": "Just finished rolling out Okta to all 180 NovaPay employees. 8 weeks, zero showstoppers, 97% enrollment in the first 24 hours. The IT gods smiled on us 🙏 #Okta #IAM #NovaPay", "date": "April 4, 2024", "likes": 67, "image_url": "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=800&q=80"},
        {"text": "PSA to all NovaPay staff: MFA is non-negotiable. I have revoked access for people before and I will do it again. Love you all, but seriously. 🔐 #MFA #SecurityAwareness", "date": "March 21, 2024", "likes": 134},
        {"text": "Home lab weekend: deployed a SIEM on my Proxmox cluster. Collected and analyzed 48 hours of logs from my own network. Found three things I didn't know about. 😬 #HomeLab #SIEM", "date": "March 17, 2024", "likes": 41},
        {"text": "Jamf Pro rollout complete for all Mac fleet. Zero-touch enrollment is genuinely magic when it works. 3 months and 94 laptops later — it works. 💻 #Jamf #MDM #IT", "date": "February 8, 2024", "likes": 52, "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80"},
        {"text": "New ServiceNow workflow live: automated password reset with identity verification. Reduces our reset tickets by 60% and adds a callback verification step. 📋 #ServiceNow #ITSM", "date": "January 30, 2024", "likes": 38},
        {"text": "Gaming night with the IT team — four hours of Catan. I will not be accepting criticism of my longest road strategy. 🎲 #TeamNight #GamerLife", "date": "April 6, 2024", "likes": 87},
        {"text": "Security reminder: if someone calls claiming to be 'IT from HQ' and asks you to give them your Okta OTP — that is not us. That is a social engineer. Call back on the internal directory. 📞 #Vishing #SecurityAwareness", "date": "March 7, 2024", "likes": 156},
        {"text": "Completed my CompTIA Security+ last weekend 🎓 Studied for 10 weeks. Next up: either SSCP or starting the OSCP grind. Leaning OSCP. #Certification #InfoSec #CyberSecurity", "date": "February 25, 2024", "likes": 93},
        {"text": "VPN vendor migration from Cisco AnyConnect to Tailscale for our remote fleet. Night and day UX for users. Night and day operational simplicity for me. 🌐 #VPN #ZeroTrust", "date": "April 14, 2024", "likes": 44},
        {"text": "Unpopular IT opinion: most 'security incidents' are just IT hygiene failures. Patch your systems. Enable MFA. Don't share passwords. That's 80% of it. #InfoSec #CISO", "date": "January 10, 2024", "likes": 211, "image_url": "https://images.unsplash.com/photo-1521737604082-c99572a3b18e?w=800&q=80"},
        {"text": "I fix 40 IT tickets a week. 35 are password resets. 4 are VPN issues. 1 is actually interesting. Today was the interesting one. 🙂 #ITLife #HelpDesk", "date": "March 13, 2024", "likes": 78},
    ],
    "omar_hassan": [
        {"text": "Found a beautiful edge case today: NovaPay's reconciliation flow silently passes if the currency code is an empty string. Zero amount, no error, transaction logged as 'completed.' Three years in production. No one noticed. I noticed. 🐛 #QA #EdgeCase", "date": "April 9, 2024", "likes": 189, "image_url": "https://images.unsplash.com/photo-1583416750470-d51bb4edc7b1?w=800&q=80"},
        {"text": "Bug bash results: team found 47 defects in 4 hours. 6 critical, 14 high, 27 medium. The ratio of 'obvious' to 'you need to think like a malicious user' was about 60/40. #QA #BugBash #NovaPay", "date": "March 25, 2024", "likes": 78},
        {"text": "Switched our E2E tests from Cypress to Playwright this sprint. The parallel execution improvement alone is worth the migration. Test suite went from 24 min to 7 min. 🎭 #Playwright #TestAutomation", "date": "February 29, 2024", "likes": 112, "image_url": "https://images.unsplash.com/photo-1629654291664-a9a13abebdfe?w=800&q=80"},
        {"text": "Mandatory QA maxim: if it can happen in staging, it will happen in prod. Run your tests in the environment that scares you most. #SoftwareTesting #QA #DevOps", "date": "March 12, 2024", "likes": 67},
        {"text": "TestRail migration complete. 1,400 test cases organized, tagged, and linked to Jira. We went from 'I think we tested that' to 'here's the traceability report.' 📊 #TestRail #QA #TestManagement", "date": "January 22, 2024", "likes": 44},
        {"text": "Interviewed a QA candidate who said they 'don't write negative test cases because the product should just work.' Reader, I did not hire them. 😐 #QAInterview #SoftwareTesting", "date": "April 5, 2024", "likes": 234},
        {"text": "Kevin (shoutout to Kevin Brooks) fixed the race condition I flagged last week before it hit prod. This is the crossover episode between backend and QA that I love. 🤝 #Teamwork #NovaPay", "date": "March 21, 2024", "likes": 55},
        {"text": "Weekend read: 'Explore It' by Elisabeth Hendrickson. For anyone who wants to level up their exploratory testing game — it's short, dense, and immediately applicable. 📖 #QA #Books", "date": "February 11, 2024", "likes": 38},
        {"text": "Staging environment is not production. But if you treat staging like it doesn't matter, production will teach you otherwise. Don't learn that lesson the hard way. #SoftwareEngineering #QA", "date": "March 2, 2024", "likes": 91},
        {"text": "NovaPay payment flow: 1,200 test cases, 98.7% pass rate on latest build. The 1.3% are all known and tracked. No surprises. That's the QA goal. 📈 #TestMetrics #QA #Fintech", "date": "April 13, 2024", "likes": 47, "image_url": "https://images.unsplash.com/photo-1590283603385-17ffb3aa346a?w=800&q=80"},
        {"text": "Family dinner tonight — turned off Slack, left the laptop at work. The bugs will still be there tomorrow. Some things matter more. ❤️ #WorkLifeBalance #Family", "date": "April 7, 2024", "likes": 103},
    ],

    # === Mini Spear Phishing — Meridian Health Partners ===
    "rachel_target": [
        {"text": "Just got back from the HIMSS Conference in Orlando! 3 days of amazing talks on healthcare data interoperability. Connected with so many great people! 🏥📊 #HIMSS2024 #HealthIT", "date": "March 15, 2024", "likes": 67},
        {"text": "Marathon training update: 14 miles this weekend! My first marathon is in October and I'm actually starting to believe I can do it 🏃‍♀️💪 #MarathonTraining #Running", "date": "April 7, 2024", "likes": 45, "image_url": "https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?w=800&q=80"},
        {"text": "Mochi update: he knocked my coffee off the desk AGAIN. At least it wasn't on my laptop this time 🐱☕ Working from home has its challenges! #CatMom #WFH", "date": "April 10, 2024", "likes": 89},
        {"text": "Big milestone at work! Our GenomicsDB project just processed its 1 millionth patient record. So proud of our team at Meridian Health Partners 🧬📈 #Genomics #HealthTech", "date": "March 28, 2024", "likes": 112, "image_url": "https://images.unsplash.com/photo-1576086213369-f5e53c4e5e4b?w=800&q=80"},
        {"text": "Sunday pho day! Made my mom's recipe from scratch — 8 hours of simmering broth. The secret ingredient is star anise and lots of love 🍜❤️ #VietnameseFood #Cooking #PhoDay", "date": "April 14, 2024", "likes": 73},
        {"text": "Apartment hunting in Capitol Hill is BRUTAL. Saw 6 places this weekend, 2 were decent but already taken by the time I applied 😩 #ApartmentHunting #CapitolHill #Seattle", "date": "April 12, 2024", "likes": 34},
        {"text": "Morning run to Blue Bottle Coffee, then back to the GenomicsDB pipeline. Living my best life ☕🏃‍♀️💻 My usual: oat milk latte, extra shot #BlueBotleCoffee #MorningRoutine", "date": "April 5, 2024", "likes": 28},
        {"text": "Shoutout to my colleague Omar Hassan for helping me debug a gnarly data pipeline issue today! Bioinformatics + good teamwork = problem solved 🔬🤝 #Teamwork #MeridianHealth", "date": "March 20, 2024", "likes": 41},
        {"text": "1 year at Meridian Health Partners today! From fresh grad to managing the entire clinical data pipeline. Thank you Dr. Whitfield for the opportunity 🎉 #WorkAnniversary", "date": "February 1, 2024", "likes": 134, "image_url": "https://images.unsplash.com/photo-1573164713988-8665fc963095?w=800&q=80"},
        {"text": "Joined a running group in Capitol Hill! Training for my first marathon with others is SO much better than running alone. Saturday 6AM long runs 🌅🏃‍♀️ #RunningCrew #Seattle", "date": "March 8, 2024", "likes": 52},
        {"text": "Attended a webinar on HIPAA compliance for genomic data. The regulatory landscape is evolving fast — we need to stay ahead 🔒📋 #HIPAA #DataPrivacy #Biotech", "date": "February 20, 2024", "likes": 19},
        {"text": "My mom visited from Houston last week. She made enough pho to last a month and taught me her secret spring roll recipe 🥰🇻🇳 I miss her already #Family #VietnameseFood", "date": "January 25, 2024", "likes": 95, "image_url": "https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?w=800&q=80"},
    ],

    # === Mini Quid Pro Quo — BrightPath Education ===
    "sandra_teacher": [
        {"text": "First day of spring semester at BrightPath Education! 3 classes of eager 10th graders. Let's make this the best year yet! 📚 #Teaching #Education", "date": "January 8, 2024", "likes": 45, "image_url": "https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=800&q=80"},
        {"text": "My students' essays on 'To Kill a Mockingbird' blew me away. These kids are so thoughtful and articulate 🦅📖 #EnglishTeacher #ProudTeacher", "date": "February 5, 2024", "likes": 67},
        {"text": "Technology in the classroom is amazing... when it works 😅 Smart board crashed during my Shakespeare presentation. Had to go old school with the whiteboard! #TeacherLife", "date": "February 15, 2024", "likes": 89},
        {"text": "Parent-teacher conferences this week. 42 meetings in 3 days. Send caffeine! ☕ #TeacherLife #ParentConferences", "date": "March 1, 2024", "likes": 34},
        {"text": "Our IT department at BrightPath is so overworked. Only 2 techs for the entire school. I always try to troubleshoot on my own before calling them 💻 #EdTech", "date": "March 10, 2024", "likes": 18},
        {"text": "Spring break reading list: currently on my 5th book! There's nothing like a week of uninterrupted reading 📚🌷 #BookNerd #SpringBreak", "date": "March 20, 2024", "likes": 53, "image_url": "https://images.unsplash.com/photo-1427504494785-3a9ca7044f45?w=800&q=80"},
        {"text": "15 years of teaching! From my first nervous day as a substitute to department head at BrightPath. Teaching is my calling ❤️ #TeacherAppreciation", "date": "April 1, 2024", "likes": 134, "image_url": "https://images.unsplash.com/photo-1606761568499-6d2451b23c66?w=800&q=80"},
        {"text": "Introduced my students to Google Docs for collaborative essays. Half the class had never used it! Digital literacy is SO important #EdTech #DigitalLiteracy", "date": "January 20, 2024", "likes": 28},
        {"text": "Friday movie day: showed the 1996 Romeo + Juliet with Leonardo DiCaprio. The students were RIVETED. Shakespeare is timeless! 🎬", "date": "February 22, 2024", "likes": 42},
        {"text": "Can someone help? My school laptop keeps freezing when I open more than 3 Chrome tabs. Is this a me problem or an IT problem? 😩 #TechTroubles", "date": "April 5, 2024", "likes": 76},
        {"text": "Garden update: my tomatoes are finally sprouting! 🍅 Teaching by day, gardening by evening. The perfect balance #GardenLife #TeacherHobbies", "date": "March 28, 2024", "likes": 31, "image_url": "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=800&q=80"},
    ],

    # === chain_of_trust — Helix Systems ===
    "carol_mitchell": [
        {"text": "Operations is the invisible architecture of a company. This week: onboarded two new SaaS vendors, coordinated a cross-team product demo, and still made it to yoga by 7:30pm. The juggle is real. #StartupOps #HelixSystems", "date": "April 8, 2025", "likes": 57, "image_url": "https://images.unsplash.com/photo-1545205597-3d9d02c29597?w=800&q=80"},
        {"text": "One thing I've learned at Helix: the best ops people are force multipliers for their technical teams. My job is to clear the path — not walk it for you. #TeamOps #PartnerOps", "date": "March 20, 2025", "likes": 83},
        {"text": "Successful vendor evaluation this week — connected our new data integration partner directly with Rachel Nguyen on the backend team. That handoff took me 4 minutes. Two months ago it would've taken two weeks. #ProcessImprovement", "date": "March 5, 2025", "likes": 42},
        {"text": "Helix's partnerships page is live! If you're a SaaS vendor evaluating our API for data integration, reach me at a.reeves@helixsystems.io — I'll get you connected to the right technical contact fast. #Partnerships #HelixSystems", "date": "February 18, 2025", "likes": 31},
        {"text": "Hot yoga Tuesday reminder: you cannot pour from an empty cup. Operations leaders — take your breaks. Block your lunch. Log off at 6. Your team needs a rested version of you, not a burned-out one. #OperationsLife", "date": "February 4, 2025", "likes": 95, "image_url": "https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?w=800&q=80"},
        {"text": "Three years at Helix Systems. From external partnership coordinator to Head of Operations. The role grew with the company — which is exactly how it should work at a startup. Grateful for every messy, fast, chaotic month. #WorkAnniversary #HelixSystems", "date": "January 15, 2025", "likes": 167, "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80"},
        {"text": "Notion tip for operations teams: keep a live vendor directory with the right technical contact at each company. It turns a 3-day email thread into a 10-minute intro call. #Notion #OpsStack", "date": "January 6, 2025", "likes": 38},
        {"text": "Morning ritual: matcha, Slack digest, standup at 9. Then the day is mine. Structure at the top of the morning pays dividends all day. #MorningRoutine", "date": "December 10, 2024", "likes": 61, "image_url": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=800&q=80"},
        {"text": "Attended a partner kickoff at the Helix office today. Reminder that remote-first doesn't mean relationship-optional. Real trust is built in the room. #PartnerOps #HelixSystems", "date": "November 22, 2024", "likes": 44},
    ],
    "chris_park": [
        {"text": "Day 60 at Helix Systems! Coming from a startup to enterprise SaaS is wild. The scale of what we're building here is honestly kind of insane. So glad I made the jump. #HelixSystems #BackendEngineering #NewJob", "date": "September 12, 2024", "likes": 41, "image_url": "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=800&q=80"},
        {"text": "Spent the whole morning tracking down a silent failure in our data pipeline. Turned out to be a timezone offset bug that only triggered on UTC+9. Three lines to fix. Twelve hours to find. Classic. #BackendEngineering #Debugging", "date": "October 28, 2024", "likes": 63},
        {"text": "Dr. James Whitfield reviewed my first major PR today. Feedback was blunt but the 30-min walkthrough afterward was gold. Best senior engineer I've worked with. #HelixSystems #CareerGrowth", "date": "September 30, 2024", "likes": 87, "image_url": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&q=80"},
        {"text": "Getting deeper into the analytics pipeline work. Can't say much but the architecture decisions we're making now are going to matter a lot in Q1. Exciting stuff. #BackendEngineering #DataPipelines", "date": "November 5, 2024", "likes": 54},
        {"text": "First time presenting in the internal platform review — definitely nervous, definitely stumbled. Dr. Whitfield said 'solid work, Nguyen' afterward and I'm choosing to frame that. #HelixSystems #TeamMoment", "date": "October 15, 2024", "likes": 49},
        {"text": "Anyone else on the team using nexus.helixsystems.io/repo/ for sharing internal build artifacts? Took me two weeks to figure out the folder structure. Austin-office folks — ping me if you need the walkthrough! #HelixSystems #InternalTools", "date": "November 18, 2024", "likes": 27},
        {"text": "Backend fun fact: you start dreaming in async/await after long enough. Last night I was literally awaiting a pizza. Send help. And also coffee. #BackendLife #PythonDev", "date": "December 3, 2024", "likes": 72},
        {"text": "Bouldering at Mission Cliffs last night. Fell off the V4 overhang three times then sent it on the fourth. Kind of a metaphor for debugging, honestly. #Bouldering #BayArea", "date": "December 18, 2024", "likes": 58, "image_url": "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=800&q=80"},
    ],
    "robert_torres": [
        {"text": "Eight years in enterprise SaaS and I still get a kick out of a clean deployment. Zero downtime, metrics flat, customers never noticed. That's the goal every time. #HelixSystems #PlatformEngineering #Grateful", "date": "October 1, 2024", "likes": 141, "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80"},
        {"text": "The platform team hit a major internal milestone this week. Details stay internal but the engineers who put in the late nights know what they built. Really proud of this group. #HelixSystems #TeamWork", "date": "November 14, 2024", "likes": 207, "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80"},
        {"text": "Engineering principle I keep coming back to: boring infrastructure is good infrastructure. If your on-call rotation is quiet, you did something right. #PlatformEngineering #SiteReliability", "date": "October 22, 2024", "likes": 93},
        {"text": "Spoke at an internal eng all-hands about data pipeline observability. Felt weird seeing my slides on a 15-foot screen. Apparently people found it useful. Maybe I'll write it up. #HelixSystems #DataEngineering", "date": "September 18, 2024", "likes": 162},
        {"text": "PSA to the team: when pushing build artifacts to nexus.helixsystems.io/repo/ — use the /releases subfolder for anything going to staging. The /dev path is for local testing only. Pinning this for the Austin team. #InternalNote #HelixSystems", "date": "November 28, 2024", "likes": 34},
        {"text": "'It works on my machine' is not a deployment strategy. If I have grey hair, it's because of that sentence. Fix it in the pipeline or don't ship it. #EngineeringCulture", "date": "December 10, 2024", "likes": 218},
        {"text": "Thursday evening: two hours at the woodworking bench. Hand-cut dovetail joint, finally clean. Engineering and craft share the same discipline — patience, precision, no shortcuts. #Woodworking #Engineering", "date": "December 20, 2024", "likes": 71, "image_url": "https://images.unsplash.com/photo-1543269664-56d93c1b41a6?w=800&q=80"},
        {"text": "Mentoring three bootcamp engineers tonight. Different level, same problems: debugging without println, thinking in systems, trusting the type checker. Worth every Thursday. #Mentorship #EngineeringCulture", "date": "November 8, 2024", "likes": 89},
    ],
    "lisa_harmon": [
        {"text": "Ran our Q4 phishing simulation at Helix. Click rate: 11% on a targeted vishing-support scenario. Better than industry average. Not good enough. Training deck going out Monday. #PhishingSimulation #SecurityAwareness #HelixSystems", "date": "April 10, 2025", "likes": 78, "image_url": "https://images.unsplash.com/photo-1583416750470-d51bb4edc7b1?w=800&q=80"},
        {"text": "Hard truth: your zero-trust policy is only as good as your help desk's verification process. I audit ours quarterly. Last quarter we found two scenarios where a caller with a manager's name and department could bypass identity checks. Fixed now. #ZeroTrust", "date": "March 28, 2025", "likes": 134},
        {"text": "Spoke at BSides SF: 'The Front Desk as an Attack Surface.' If you train only engineers and skip operations, the attacker goes straight for operations. Obvious in retrospect. Still rare to fix in practice. #BSidesSF #SocialEngineering", "date": "March 12, 2025", "likes": 189, "image_url": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&q=80"},
        {"text": "Quarterly tabletop exercise complete. Scenario: phone chain — operations staff → junior engineer → platform lead. The good news: our leadership now understands why I run these every quarter, not annually. #IncidentResponse #ThreatModeling", "date": "February 20, 2025", "likes": 97},
        {"text": "Passed the CISSP renewal exam. Six hours. 250 questions. Four espressos. Still worth it. Security knowledge has a half-life — keep it current. #CISSP #CyberSecurity", "date": "February 5, 2025", "likes": 143, "image_url": "https://images.unsplash.com/photo-1521737604082-c99572a3b18e?w=800&q=80"},
        {"text": "PSA: I am the IT Security Manager. Ext. 4001. If anything feels off — a caller asking for access, an email requesting credentials, a 'colleague' you can't verify — call me. Escalate early. #HelixSystems #SecurityCulture", "date": "January 15, 2025", "likes": 82},
        {"text": "CTF recap from this weekend: three social engineering forensics challenges, one vishing audio reconstruction. If you're a security practitioner who doesn't do CTFs, you're leaving defense gaps. #CTF #InfoSec", "date": "December 8, 2024", "likes": 56},
        {"text": "Co-finalized Helix's incident response playbook — 47 pages, 12 scenarios. The scenario that generated the most debate? Phone-chain vishing targeting junior engineers. Tells you something about where our real risks live. #IncidentResponse", "date": "November 17, 2024", "likes": 112},
        {"text": "Monthly reminder: I run callback verification on ALL access requests. Yes, even from senior engineers. Yes, even on Fridays. The urgency framing is the red flag, not the request itself. #SecurityMindset #HelixSystems", "date": "October 8, 2024", "likes": 93},
    ],
    "mike_donahue": [
        {"text": "Helix staging environment is fully automated. Terraform + GitHub Actions + ArgoCD. What used to take 45 minutes takes 8 minutes and a PR merge. Dr. Whitfield called it 'transformative'. I called it 'finally'. #DevOps #IaC #HelixSystems", "date": "April 3, 2025", "likes": 87, "image_url": "https://images.unsplash.com/photo-1629654291664-a9a13abebdfe?w=800&q=80"},
        {"text": "Reminder to the engineering team: ALL environment access requests need a ticket. Even if it's small. Even if Dr. Whitfield asks me in the hallway. I love you all — but I need the paper trail. #DevOps #AccessManagement", "date": "March 18, 2025", "likes": 62},
        {"text": "kubectl (my cat) knocked over my laptop mid-deploy today. Incident severity: P2 (personal). She is unrepentant. #DevOps #CatLife", "date": "February 28, 2025", "likes": 201, "image_url": "https://images.unsplash.com/photo-1495360010541-f48722b35f7d?w=800&q=80"},
        {"text": "Hiking the Dipsea Trail Saturday. If the NEXUS staging pipeline breaks before I'm back Sunday, there's a runbook and you know where to find me on Slack. Happy trails, humans. #HikingMarin #DevLife", "date": "February 15, 2025", "likes": 54, "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80"},
        {"text": "Kubernetes upgrade to 1.30 complete on all staging clusters. Zero downtime. Zero alerts. Zero drama. This is the goal. #Kubernetes #SRE #HelixSystems", "date": "February 5, 2025", "likes": 68, "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80"},
        {"text": "New house rule: no manual deployments after 4pm on Fridays. The person who breaks this rule buys the team's coffee. Third time this month. You know who you are. #DevOpsCulture #NoProdFridays", "date": "January 24, 2025", "likes": 76},
        {"text": "Home automation update: my K3s home cluster now automatically dispatches my morning coffee order at 7am. Yes I am fine. #HomeLab #Kubernetes #Automation", "date": "January 10, 2025", "likes": 148},
        {"text": "CI/CD pipeline review: cut average build time from 14min to 6min by parallelizing the test suite. Small change, big quality-of-life improvement for the whole engineering team. #CICD #Performance", "date": "December 12, 2024", "likes": 53},
        {"text": "Dr. Whitfield and I ran a full staging-to-prod rehearsal for the NEXUS v2 rollout today. Playbook: execute. The platform is in good hands. #HelixSystems #PlatformEngineering", "date": "November 27, 2024", "likes": 91},
        {"text": "Grew up in Seattle, now in Alameda. The weather is better. The traffic is the same. kubectl (the cat) approves of the apartment's natural light, which she uses exclusively for napping. #BayArea #CatLife", "date": "November 5, 2024", "likes": 67},
    ],

    # === mini_authority — GreenLeaf Biotech ===
    "robert_chen": [
        {"text": "GreenLeaf's drought-resistant sorghum just passed Phase 3 trials in Sub-Saharan Africa. Three years of work, 200+ field sites, zero fatalities in the trial cohorts. Proud doesn't cover it. #Biotech #SustainableAg", "date": "April 10, 2024", "likes": 312, "image_url": "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=800&q=80"},
        {"text": "To every founder who told me 'biotech is too slow for a startup': we just closed a $90M Series C in 18 months from seed. Discipline beats pace. #BiotechVC #Startup", "date": "March 28, 2024", "likes": 287, "image_url": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=800&q=80"},
        {"text": "Board meeting this week. The team presented genomics pipeline results that genuinely surprised even me. When your scientists surprise you, you've hired the right scientists. #Leadership #GreenLeaf", "date": "March 15, 2024", "likes": 198},
        {"text": "Keynote at BIO International next month. Topic: 'From Lab to Field: Closing the Sustainable Agriculture Gap in 5 Years.' First time I'll talk publicly about the Phase 3 data. #BIO2024", "date": "March 1, 2024", "likes": 143, "image_url": "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?w=800&q=80"},
        {"text": "Had a long call with Margaret Sullivan about the CRISPR regulatory timeline. The compliance calendar is the real product roadmap in this industry. #Biotech #Regulation", "date": "February 18, 2024", "likes": 89},
        {"text": "Six years ago I quit a tenured position to start GreenLeaf. My former department head said it was 'career suicide.' Today we employ 240 scientists. Risk tolerance is a skill. #FounderLife", "date": "February 1, 2024", "likes": 445, "image_url": "https://images.unsplash.com/photo-1576086213369-f5e53c4e5e4b?w=800&q=80"},
        {"text": "Reminder to the team: the Q3 revenue report contains forward-looking projections that are NOT for external circulation. All media inquiries go through Linda Hayes. #GreenLeaf #OPSEC", "date": "January 20, 2024", "likes": 34},
        {"text": "The agriculture sector is about to go through the same transformation genomics brought to medicine. GreenLeaf is building the platform for that transition. 10 years from now this will be obvious. Now it still isn't. #Vision", "date": "January 8, 2024", "likes": 567},
    ],
    "linda_hayes": [
        {"text": "Coordinating Dr. Chen's BIO International keynote logistics. 3 cities, 2 panel sessions, 1 media interview with Nature Biotechnology — all in 4 days. This is my sport. #ExecutiveAssistant #Biotech", "date": "March 5, 2024", "likes": 47},
        {"text": "PSA to external contacts: all media and investor inquiries for Dr. Robert Chen go through linda.hayes@greenleaf.com (me!). Direct outreach goes to voicemail. This is intentional. 😊 #Scheduling", "date": "February 22, 2024", "likes": 29, "image_url": "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=800&q=80"},
        {"text": "5 years supporting C-suite executives across three industries. The #1 skill? Knowing which meetings to protect them from. The #2 skill? Knowing which ones they're avoiding but shouldn't. #EALife", "date": "February 8, 2024", "likes": 63},
        {"text": "Board prep week. 47 slides, 3 appendix decks, 2 revised P&L projections, and one very determined CFO. Love this organized chaos. #GreenLeaf", "date": "January 30, 2024", "likes": 38},
        {"text": "Attended an EA network event last night. The amount of institutional knowledge in that room — the real decisions of every major company flow through people like us. #ExecutiveAssistant", "date": "January 18, 2024", "likes": 84, "image_url": "https://images.unsplash.com/photo-1434626881859-51f326ccc3a4?w=800&q=80"},
        {"text": "Out of office coverage: Dr. Chen is traveling this week for investor meetings. Urgent matters — call me directly on ext. 1001. Non-urgent — Tuesday. #GreenLeaf", "date": "April 5, 2024", "likes": 12},
        {"text": "Just finalized Dr. Chen's interview schedule with Nature Biotechnology. The Phase 3 data story is going to be huge when it goes public. Can't wait for the embargo to lift. #Biotech #Exciting", "date": "March 20, 2024", "likes": 28, "image_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=800&q=80"},
    ],
    "mark_wilson": [
        {"text": "Our genomics pipeline processed 50,000 gene expression samples this quarter using a custom Spark cluster on AWS. P95 job completion: under 40 minutes. This time last year: 4 hours. #DataEngineering #Biotech", "date": "April 8, 2024", "likes": 78, "image_url": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=800&q=80"},
        {"text": "Heads up team: I'm OOO today for a family commitment. Priya is covering daily pipeline monitoring — all anomaly alerts should go to her until tomorrow. Mark.wilson@greenleaf.com for urgent only. #GreenLeaf", "date": "March 25, 2024", "likes": 14},
        {"text": "Just published our internal ML model card for the crop yield prediction system. Every model that ships needs one. Feature drift will get you if interpretability doesn't. #MLOps #DataScience", "date": "March 12, 2024", "likes": 112, "image_url": "https://images.unsplash.com/photo-1590283603385-17ffb3aa346a?w=800&q=80"},
        {"text": "Priya Sharma just delivered her first solo analysis report on the Phase 2 trial gene expression data. Six months in and already producing work at senior level. Worth investing in junior talent. #Mentorship", "date": "February 28, 2024", "likes": 89},
        {"text": "Hot take: in life sciences data, cleaning is 80% of the work and 0% of the career conversations. We need to change that. #DataQuality #Bioinformatics", "date": "February 14, 2024", "likes": 134, "image_url": "https://images.unsplash.com/photo-1554224155-8d04cb24ef21?w=800&q=80"},
        {"text": "Quarterly review: our data team delivered 12 analysis reports, 3 pipeline upgrades, and zero data breaches in Q1. The last metric is the most important. #DataTeam #GreenLeaf", "date": "April 2, 2024", "likes": 56},
        {"text": "The Q3 revenue projections Priya worked on are under strict NDA — reminder to ALL data team members that external sharing requires CFO sign-off. No exceptions, not even for 'harmless' questions. #DataGovernance", "date": "January 25, 2024", "likes": 31},
    ],
    "susan_bell": [
        {"text": "Phase 3 trial results are in. Our drought-resistant gene stack showed 38% yield improvement with 55% reduced irrigation in the Kenya trial cohorts. These numbers will go to Nature next quarter. #ResearchWin #GreenLeaf", "date": "April 5, 2024", "likes": 423, "image_url": "https://images.unsplash.com/photo-1535957998253-26ae1ef29506?w=800&q=80"},
        {"text": "Eight years building the GreenLeaf R&D function from 3 researchers to 140. The thing I'm most proud of: we've never had a reproducibility failure on a published result. Culture is a scientific asset. #Research #Leadership", "date": "March 22, 2024", "likes": 289, "image_url": "https://images.unsplash.com/photo-1576086213369-f5e53c4e5e4b?w=800&q=80"},
        {"text": "CRISPR review board cleared our drought-tolerance construct for field trials in two additional geographies. Legal + regulatory + science alignment in one week. Record time. #CRISPRag #GreenLeaf", "date": "March 8, 2024", "likes": 167},
        {"text": "Mentoring 6 early-career researchers this year. The question I always ask in our first session: 'What would you work on if you couldn't fail?' The answers predict who will do the breakthrough work. #Mentorship", "date": "February 20, 2024", "likes": 198, "image_url": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&q=80"},
        {"text": "Speaking at ISAAA next month on regulatory frameworks for genome-edited crops. The science is there. The policy is 10 years behind. Let's close that gap. #AgBiotech #Policy", "date": "February 5, 2024", "likes": 134},
        {"text": "Reminder to the lab: all genomic sequences and trial data are logged in the secure repository under your PI's directory. No data leaves the building on personal devices. Dr. Chen is strict on this. #DataSecurity #GreenLeaf", "date": "January 15, 2024", "likes": 45},
        {"text": "Saturday morning: reviewing the Phase 3 statistical models with a coffee. The peer reviewers are going to push hard on the soil composition confounds. Good. That's exactly the pressure we need. #Science #GreenLeaf", "date": "April 13, 2024", "likes": 76},
    ],

    # === human_chain — Meridian Capital Partners ===
    "ben_morgan": [
        {"text": "Closed the Lighthouse deal. Can't name the asset yet but the return profile on the infrastructure tranche is the best we've seen in seven years. The team has earned a real celebration. #MeridianCapital #PE", "date": "April 9, 2024", "likes": 387, "image_url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80"},
        {"text": "FinTech Forward keynote confirmed for next month. Looking forward to sharing our infrastructure thesis — best signal-to-noise ratio in the space. Churchill has already judged the slides. 🐕 #FinTechForward #PrivateCredit", "date": "April 5, 2024", "likes": 234},
        {"text": "Quick note: I've been using voice notes in DMs for async team updates instead of typing walls of text. More context, better tone, half the back-and-forth. Try it. 🎙️ #TeamComms", "date": "April 3, 2024", "likes": 89},
        {"text": "FinTech Forward keynote confirmed: 'Private Capital in a Rate-Volatile World.' Honored to represent the LP perspective at this level. If you're attending, come find me. #FinTechForward #PE", "date": "March 28, 2024", "likes": 189},
        {"text": "Ironman Arizona in November. At mile 18 of the marathon last year I told myself 'never again.' Currently at mile 3 of today's long run. We keep going. #Triathlon #IronmanAZ", "date": "March 20, 2024", "likes": 147, "image_url": "https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?w=800&q=80"},
        {"text": "AUM crossed $4.8B this quarter. In 2018 we managed $400M and I had a team of 6. Compound growth is the most powerful force in investing — and in building firms. #MeridianCapital #AssetManagement", "date": "March 5, 2024", "likes": 312, "image_url": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=800&q=80"},
        {"text": "Bloomberg interview on 'GP consolidation in the lower middle market.' Two quotes they didn't use: (1) scale is overrated, (2) the best LPs make you better. Both true. #PrivateEquity #Investing", "date": "February 15, 2024", "likes": 198},
        {"text": "New LP commitments this quarter came from three sovereign wealth funds and a major university endowment. Institutional trust is earned over decades. Protect it every single day. #MeridianCapital", "date": "January 30, 2024", "likes": 267, "image_url": "https://images.unsplash.com/photo-1554224155-8d04cb24ef21?w=800&q=80"},
        {"text": "Churchill turned 4 today. Attempted a celebratory run. He made it 400 meters before sitting down and refusing to move. Non-negotiable. Happy birthday, old man. 🐕‍🦺 #EnglishBulldog #AdoptDontShop", "date": "January 12, 2024", "likes": 445},
    ],
    "rachel_park": [
        {"text": "Ben's Bloomberg interview goes live at 2pm EST tomorrow. Setting 47 reminders. Also confirming his CNBC segment for Thursday. Media week is its own kind of marathon. #EA #ExecutiveLife", "date": "April 4, 2024", "likes": 38},
        {"text": "Coordinating the LP Annual Meeting logistics — 200 attendees, 3 breakout sessions, and one CEO who has strong opinions about the order of the agenda slides. This is my element. #EventPlanning #MeridianCapital", "date": "March 26, 2024", "likes": 52, "image_url": "https://images.unsplash.com/photo-1434626881859-51f326ccc3a4?w=800&q=80"},
        {"text": "Pro tip for anyone supporting a C-level: the most important skill isn't scheduling. It's knowing which meetings to protect them from before they know they need protecting. #EALife", "date": "March 14, 2024", "likes": 89},
        {"text": "FinTech Forward conference prep begins. Ben is keynoting. My job: pre-read every attendee bio, flag the five people worth an introduction, and make sure Churchill photos are approved for social media. Yes, really. 🐕 #FinTechForward", "date": "March 2, 2024", "likes": 63, "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80"},
        {"text": "A journalist from Forbes called asking for Ben's travel schedule next week 'just for context.' Transferred to comms. This is exactly why we have a comms team. #MediaTraining #MeridianCapital", "date": "February 20, 2024", "likes": 47},
        {"text": "Booking Ben's participation in the FinTech Forward 'Fireside Chat' track. They asked for three talking points. I sent twelve and he approved nine. We're ready. #MeridianCapital #FinTech", "date": "February 5, 2024", "likes": 29},
        {"text": "Five years as EA to Ben Morgan. What I've learned: the calendar is the strategy. If it's on the calendar it's a priority. If it's not, it isn't. Everything else is noise. #ExecutiveAssistant #CareerLessons", "date": "January 22, 2024", "likes": 134, "image_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=800&q=80"},
    ],
    "james_cole": [
        {"text": "Q1 close complete. Wire reconciliation across 14 fund entities took 3 days less than last year after automating the waterfall calculations. Efficiency compounds. #FinanceOps #PrivateEquity", "date": "April 3, 2024", "likes": 56, "image_url": "https://images.unsplash.com/photo-1590283603385-17ffb3aa346a?w=800&q=80"},
        {"text": "Reminder to all PMs: wire transfer authorizations over $500K require dual approval — Ben's verbal confirmation is NOT sufficient. The policy is the policy. Call me back on my direct line to confirm. #InternalControls", "date": "March 21, 2024", "likes": 23},
        {"text": "Project Lighthouse escrow documents are finalized. James Cole, Finance Director, ext. 2200 for anything requiring fund-level wire coordination this week. Very time-sensitive. #MeridianCapital #PE", "date": "March 10, 2024", "likes": 18},
        {"text": "30 years in finance. First 10 in banking, 10 in corporate treasury, 10 in private equity. Each decade taught me one thing: controls exist because humans fail under pressure. Respect the controls. #Finance #Leadership", "date": "February 28, 2024", "likes": 78, "image_url": "https://images.unsplash.com/photo-1554224155-8d04cb24ef21?w=800&q=80"},
        {"text": "LP capital call notices for Q2 went out today. $180M across 9 fund vehicles. Clean, on time, zero errors. The operations team doesn't get enough credit. #FundOps #MeridianCapital", "date": "February 12, 2024", "likes": 44},
        {"text": "Finance team offsite in Scottsdale. Two days of process reviews, one very good steak dinner, zero PowerPoint slides by day 2. Productive. #TeamBuilding #Finance", "date": "January 30, 2024", "likes": 67, "image_url": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&q=80"},
        {"text": "Completed the annual SOC 1 Type II audit with zero findings for the third consecutive year. You don't get three in a row without a team that takes controls seriously every single day. #Audit #MeridianCapital", "date": "January 10, 2024", "likes": 89},
    ],
    "sarah_whitfield": [
        {"text": "Attended a CEO + CFO security briefing on deepfake voice fraud targeting financial executives. The demo was genuinely unsettling. If anyone calls requesting an expedited wire — call me back on my known number first. Always. #FraudPrevention", "date": "April 7, 2024", "likes": 198, "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&q=80"},
        {"text": "My verification protocol for any unusual payment request: (1) end the call (2) find the requester's number in the company directory (3) call back from my desk phone. Three steps. Non-negotiable. Saved us $2.1M last quarter. #CFO #FraudPrevention", "date": "March 26, 2024", "likes": 312, "image_url": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=800&q=80"},
        {"text": "Speaking at CFO Summit on 'AI voice cloning and wire fraud: the new threat model for treasury functions.' If your organization hasn't updated controls for deepfake threats, you're already behind. #CFOSummit #Cybersecurity", "date": "March 12, 2024", "likes": 234},
        {"text": "We've had three social engineering attempts on our finance team in 18 months. None succeeded. That's not luck — it's verification culture, tabletop exercises, and zero tolerance for 'urgent exceptions.' #Finance #Security", "date": "February 20, 2024", "likes": 156},
        {"text": "Quarterly review for all treasury staff: verbally confirm every out-of-policy transaction directly with the requestor. No exceptions for urgency, seniority, or 'the CEO needs it now.' ESPECIALLY not that last one. #TreasuryOps", "date": "February 5, 2024", "likes": 89},
        {"text": "CFA Institute panel last week on financial controls in the AI era. The scariest thing in that room: most firms still use email as their sole wire approval channel. Terrifying. #CFA #FinancialControls", "date": "January 22, 2024", "likes": 178, "image_url": "https://images.unsplash.com/photo-1434626881859-51f326ccc3a4?w=800&q=80"},
        {"text": "End of year: our team processed $3.2B in fund transactions with zero errors, zero fraud losses, and zero policy exceptions. I'm proud of every person in this department. #MeridianCapital #YearEnd", "date": "December 31, 2023", "likes": 267},
    ],
    "alex_reed": [
        {"text": "We blocked a vishing attempt yesterday targeting our finance team. Caller claimed to be a vendor, knew our CFO's name, and had our main number. OSINT-prepped and convincing. The tell: they couldn't pass our callback protocol. Train your callbacks. #InfoSec #Vishing", "date": "April 11, 2024", "likes": 234, "image_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&q=80"},
        {"text": "PSA: Caller ID is trivially spoofed. If someone calls claiming to be a colleague and requests an unusual action — hang up. Find their number in the directory. Call back. This is not paranoia. This is the minimum. #PhoneSecurity", "date": "March 30, 2024", "likes": 312, "image_url": "https://images.unsplash.com/photo-1521737604082-c99572a3b18e?w=800&q=80"},
        {"text": "Deepfake voice cloning has crossed the 'convincing to untrained humans' threshold. We're running tabletop exercises next month on exactly this scenario. Every financial controls team in PE should be doing the same. #Deepfake #InfoSec", "date": "March 16, 2024", "likes": 187},
        {"text": "Completed our annual penetration test. Red team used a spear-phishing pretext so good even I almost forwarded it. The scary ones feel personal because they are — they OSINT you first. #PenTest #RedTeam", "date": "February 25, 2024", "likes": 145},
        {"text": "OSINT on yourself: searched my name, firm, and role combination on LinkedIn. Found enough public info to build a convincing pretext in under 20 minutes. Your attackers have already done this. #OSINT #Security", "date": "February 10, 2024", "likes": 289, "image_url": "https://images.unsplash.com/photo-1583416750470-d51bb4edc7b1?w=800&q=80"},
        {"text": "Endpoint fleet is now fully on CrowdStrike Falcon with custom detections for financial application anomalies. The finance team hates the extra auth steps. I'm fine with that. #EndpointSecurity #CrowdStrike", "date": "January 28, 2024", "likes": 98},
        {"text": "Security awareness stat from our last simulation: 12% of staff clicked a spear-phishing link when the email mentioned their manager by name and referenced a real project. OSINT makes phishing dangerous. Train for it. #SecurityAwareness", "date": "January 12, 2024", "likes": 178},
    ],

    # === mini_quid_pro_quo — BrightPath Education ===
    "principal_margaret_hayes": [
        {"text": "Proud to announce BrightPath's 3rd consecutive year of 'Distinguished School' designation from the state Board of Education. This belongs to every teacher, student, and parent in our community. 🏫 #BrightPath #Education", "date": "April 8, 2024", "likes": 312, "image_url": "https://images.unsplash.com/photo-1606761568499-6d2451b23c66?w=800&q=80"},
        {"text": "Parent-teacher conference week complete. 400+ family conversations in 4 days. The most important part of educational leadership isn't curriculum — it's community trust. Grateful for every family that showed up. #BrightPath", "date": "March 22, 2024", "likes": 178, "image_url": "https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=800&q=80"},
        {"text": "Reminder to all staff: all technology requests, software installs, and device issues go through John Carter in IT (ext. 6050) or via the helpdesk portal. Please don't try to resolve tech issues independently — we've had security incidents that way. #BrightPath #CyberSafety", "date": "March 8, 2024", "likes": 67},
        {"text": "30 years in education. 8 as a teacher, 12 as VP, 10 as Principal. The thing that hasn't changed: the students who need the most aren't always the loudest. Education is about seeing all of them. #PrincipalLife #Education", "date": "February 25, 2024", "likes": 234, "image_url": "https://images.unsplash.com/photo-1427504494785-3a9ca7044f45?w=800&q=80"},
        {"text": "BrightPath's new digital literacy curriculum launches next semester. In an era of deepfakes and AI content, teaching students to critically evaluate sources is more important than any STEM topic. #DigitalLiteracy #EdTech", "date": "February 10, 2024", "likes": 145},
        {"text": "Security reminder from John Carter's IT team: BrightPath will NEVER ask for your Microsoft 365 password via email. If you receive such a request — report it to IT immediately. We take phishing seriously. #CyberSecurity #BrightPath", "date": "January 28, 2024", "likes": 89},
        {"text": "Teacher Appreciation Week starts Monday. If you know a BrightPath educator — reach out. The work they do is invisible to most and essential to everyone. #TeacherAppreciation #BrightPath", "date": "April 14, 2024", "likes": 198},
    ],
    "john_carter": [
        {"text": "Deployed Microsoft Intune across all 180 BrightPath staff devices this week. Zero-touch enrollment, BitLocker on all endpoints, conditional access policies live. IT hygiene is school safety. #Intune #EdTech #IT", "date": "April 6, 2024", "likes": 67},
        {"text": "PSA to all BrightPath staff: IT will NEVER ask for your Microsoft 365 password. Via email, via phone, via person. If anyone claiming to be IT asks for your password — it is not IT. Call me on ext. 6050 to verify anything suspicious. #Phishing #Security", "date": "March 24, 2024", "likes": 134},
        {"text": "Blocked a phishing campaign targeting our teachers last week. The lure: a 'free security scan' email with a convincing Microsoft logo. 3 teachers clicked. None entered credentials thanks to MFA. MFA saves lives (professionally). #Phishing #BrightPath", "date": "March 10, 2024", "likes": 89, "image_url": "https://images.unsplash.com/photo-1521737604082-c99572a3b18e?w=800&q=80"},
        {"text": "Device refresh complete: 40 new Dell laptops deployed for the 10th grade cohort. Each one configured, encrypted, and enrolled in Intune before it touched a student's hands. This is the job. #EdTech #ITAdmin", "date": "February 28, 2024", "likes": 45},
        {"text": "Annual cybersecurity training for BrightPath staff complete. 94% pass rate on the phishing simulation. The 6% who clicked are getting individual coaching. No shame — just training. #SecurityAwareness #Education", "date": "February 14, 2024", "likes": 56, "image_url": "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=800&q=80"},
        {"text": "Reminder: the helpdesk portal is help.brightpath.com. If you're having Microsoft 365 issues, submit a ticket there. Don't click links in emails claiming to fix your account — those are almost always phishing. #IT #BrightPath", "date": "January 30, 2024", "likes": 38},
        {"text": "Running a 'spot the phish' exercise with the English department next week. Sandra Williams actually ASKED for advanced training after the last simulation. Love working with teachers who take this seriously. #SecurityTraining #BrightPath", "date": "April 12, 2024", "likes": 72, "image_url": "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=800&q=80"},
    ],
    "emily_foster": [
        {"text": "My AP Chemistry class just completed their independent research projects. 24 students, 24 original hypotheses, 24 lab notebooks that would make me proud at any university level. These kids are going to change things. 🔬 #Teaching #STEM", "date": "April 10, 2024", "likes": 89, "image_url": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=800&q=80"},
        {"text": "Three BrightPath students placed in the regional Science Olympiad this weekend. All three were in my intro chemistry class two years ago. Watching students grow from 'what is a covalent bond' to competition level is the whole point of this job. #ScienceOlympiad", "date": "March 28, 2024", "likes": 134, "image_url": "https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=800&q=80"},
        {"text": "New lab equipment arrived! Spectrophotometers, digital pH meters, and a gas chromatography setup that I have absolutely no budget excuse for anymore. Time to update the curriculum. #ChemistryTeacher #BrightPath", "date": "March 14, 2024", "likes": 67},
        {"text": "Parent asked me this week if my class was 'too hard.' My answer: the hard part isn't the chemistry. It's learning how to be wrong, adjust, and try again. That's the actual lesson. Science is just the medium. #TeacherLife #GrowthMindset", "date": "February 29, 2024", "likes": 178},
        {"text": "Wrote my first grant proposal for a student research stipend program. If funded, 10 BrightPath students will run paid independent research projects over the summer. Fingers crossed. 🤞 #STEM #BrightPath", "date": "February 15, 2024", "likes": 93},
        {"text": "PhD in physical chemistry. 8 years in industry research. 6 years teaching high school. Objectively the most intellectually demanding job is the one with 30 confused 16-year-olds who need to understand thermodynamics by Friday. #TeacherLife", "date": "January 25, 2024", "likes": 215, "image_url": "https://images.unsplash.com/photo-1427504494785-3a9ca7044f45?w=800&q=80"},
        {"text": "Book rec for science teachers: 'The Art of Teaching Science' by Jack Hassard. Changed how I think about lab design. Required reading for anyone moving from research to classroom. #TeacherReads #STEM", "date": "January 10, 2024", "likes": 56},
    ],
    "carlos_rivera": [
        {"text": "End of semester stats: 87% of my Algebra II students improved their grade by at least one letter compared to their Algebra I final. The tutoring program we started in September worked. Data doesn't lie. 📊 #MathTeacher #BrightPath", "date": "April 12, 2024", "likes": 134},
        {"text": "Saturday morning tutoring session: 8 students, 3 hours, and a genuine breakthrough on quadratic functions for a kid who's been struggling all semester. This is the moment you teach for. #Math #Tutoring", "date": "March 30, 2024", "likes": 89, "image_url": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=800&q=80"},
        {"text": "My Calculus BC students are asking questions I don't have instant answers to. That's when you know the class is working. #APCalc #Teaching #BrightPath", "date": "March 16, 2024", "likes": 76},
        {"text": "Coaching the Math Team to regionals next month! 12 students who voluntarily do math problems on their lunch break. These are my people. 🧮 #MathTeam #BrightPath", "date": "March 2, 2024", "likes": 112, "image_url": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&q=80"},
        {"text": "Redesigned my entire stats curriculum to use real datasets — sports analytics, public health data, economic trends. Students are engaged when the numbers are about something they care about. #Statistics #DataLiteracy", "date": "February 18, 2024", "likes": 98},
        {"text": "10 years teaching. The students who said 'I'm not a math person' in September who are now tutoring their peers by May — that's the reason for all of it. #MathTeacher #Growth", "date": "February 2, 2024", "likes": 167, "image_url": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=800&q=80"},
        {"text": "Filed my supply request for graphing calculators. John Carter in IT says the new devices should also integrate with our digital tools. Hoping for approval before AP exam season. #BrightPath #TeacherNeeds", "date": "January 20, 2024", "likes": 34},
    ],
}

# Posts for non-persona employees (generic but industry-appropriate)
GENERIC_POSTS = {
    "IT": [
        {"text": "Another day, another server migration. Stayed until 9pm but the deployment went clean. Love this chaos. 💻 #ITLife", "date": "March 15, 2024", "image_url": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=800&q=80"},
        {"text": "Just passed my Azure Administrator certification exam! Three months of weekend studying, zero regrets. Next up: Security+. 🎓", "date": "February 20, 2024"},
        {"text": "Patch Tuesday is my favorite day... said no one ever 😅 But seriously — patch your systems. Every. Week. #SysAdmin", "date": "March 12, 2024"},
        {"text": "Home lab weekend update: finally got my Kubernetes cluster stable after two weeks of fighting CNI plugins. Home labs build real skills. 🏠🖥️", "date": "January 25, 2024"},
        {"text": "Coffee count today: ☕☕☕☕ — 4 cups and counting. It's a production deployment day. No regrets. #DevOps", "date": "March 28, 2024"},
        {"text": "Attended a solid webinar on Zero Trust network architecture. The shift from perimeter-based security to identity-based access is overdue everywhere. 🔒 #ZeroTrust", "date": "February 8, 2024", "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&q=80"},
        {"text": "PSA: 'Have you tried turning it off and on again?' Works 90% of the time. The other 10% is why I have a job.", "date": "April 2, 2024"},
        {"text": "IT networking event last night — connected with 20+ local tech leads. The local IT community here is genuinely strong. 🔥 #Networking", "date": "January 30, 2024"},
        {"text": "Weekend project: automated my home setup with Home Assistant. Now my lights literally respond to my Slack status. My family is thrilled (they're not). 😂", "date": "March 8, 2024"},
        {"text": "Reminder to everyone: always backup BEFORE you update firmware. Do not learn from my pain. Do not make my mistakes. 😭 #Backups #ITLessons", "date": "April 10, 2024", "image_url": "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=800&q=80"},
    ],
    "Marketing": [
        {"text": "Q1 campaign results are in — 34% increase in engagement YoY. Data-driven creative is the only kind of creative that scales. 📊 #Marketing", "date": "April 3, 2024", "image_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80"},
        {"text": "Content calendar for Q2 locked. Six campaigns, four channels, one very organized spreadsheet. Let's go. ✨ #ContentMarketing", "date": "March 30, 2024"},
        {"text": "Attended a brand strategy workshop this weekend. Key takeaway: consistency over time beats cleverness in the moment. Brands are built in years not campaigns. 👑", "date": "March 15, 2024"},
        {"text": "A/B tested our email subject lines this month. Adding the recipient's first name increased open rates by 22%. Personalization still works. 📧 #EmailMarketing", "date": "February 25, 2024"},
        {"text": "Marketing team offsite! Best ideas come when you get out of the building. Two full days, zero laptops at the table. 🍕 #TeamBuilding", "date": "February 10, 2024", "image_url": "https://images.unsplash.com/photo-1537511446984-935f663eb1f4?w=800&q=80"},
        {"text": "Just rolled out a new attribution model. Took 6 weeks to build, 20 minutes to present, and will immediately improve how we allocate $800K quarterly. Worth it. 📈", "date": "January 28, 2024"},
        {"text": "Creative block hit hard this week. Took a 3-mile walk, came back with a campaign concept that made the whole team stop and say 'yes.' Nature works. 🌿", "date": "March 22, 2024"},
        {"text": "Social media engagement hit an all-time record this month. The video series we were nervous about? 4.2M impressions. Trust the creative. 💪 #SocialMedia", "date": "April 8, 2024"},
        {"text": "Brand guidelines update complete — 47 pages covering voice, visual identity, and tone across every channel. Consistency at scale is underrated. 🎨", "date": "January 15, 2024"},
        {"text": "Reading 'Building a StoryBrand' by Donald Miller. If your marketing doesn't make the customer the hero, start over. Highly recommend. 📖", "date": "February 18, 2024"},
    ],
    "HR": [
        {"text": "Onboarded 5 new team members this month. Every person walked out of day one knowing their manager, their tools, and what success looks like in 90 days. That's the bar. 🎉 #HR #Onboarding", "date": "April 1, 2024", "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80"},
        {"text": "Employee engagement survey results: 89% satisfaction rate. The three lowest-scoring areas are now Q2 priorities. Scores tell you where to look. Culture tells you what you'll find. ❤️", "date": "March 20, 2024"},
        {"text": "Planning our summer team retreat. The top-voted option: mountains + hiking + no PowerPoint presentations. Easy decision. 🏔️ #TeamCulture", "date": "March 10, 2024"},
        {"text": "Just completed a two-day inclusive hiring workshop. The research is clear: diverse interview panels significantly reduce bias in hiring decisions. Implementing next month. 🌍", "date": "February 15, 2024"},
        {"text": "Benefits enrollment deadline is April 30th! If you haven't reviewed your health plan, dental, and 401k elections — do it today. Don't leave money on the table. 📋 #HR", "date": "March 1, 2024"},
        {"text": "National Employee Appreciation Day! I'm biased but: our people are genuinely exceptional. Not just productive — kind, collaborative, and curious. That doesn't happen by accident. 🌟", "date": "March 5, 2024"},
        {"text": "DEI training session drew 94% voluntary participation. When people show up without being mandated, you know the culture is real. 🤝 #Inclusion", "date": "January 22, 2024", "image_url": "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=800&q=80"},
        {"text": "Three new roles posted today — Product, Engineering, and Sales. We're growing faster than the plan said we would. Good problem to have. 🚀 #Hiring", "date": "April 5, 2024"},
        {"text": "Mental health at work matters. Our new EAP program is live with 8 free counseling sessions per employee per year. Use it. No stigma here. 🧘", "date": "February 28, 2024"},
        {"text": "Exit interviews this quarter revealed a theme: career growth visibility. We're fixing the promotion rubric before next cycle. Data from departures is data. 💬", "date": "March 25, 2024"},
    ],
    "Finance": [
        {"text": "Quarter close complete — clean reconciliation for the 12th consecutive quarter. The spreadsheets never lie and neither do we. 📊 #Finance", "date": "April 2, 2024", "image_url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80"},
        {"text": "Tax season survival kit: noise-canceling headphones, cold brew, and a closed calendar for the next 6 weeks. Let's go. ☕🧮 #TaxSeason", "date": "March 15, 2024"},
        {"text": "Attended a financial modeling masterclass this weekend. One new shortcut alone will save me 30 minutes per model. Always be learning. 📈 #Excel #Finance", "date": "February 20, 2024"},
        {"text": "FY2025 budget planning kicks off next week. Started the variance analysis on Q1 actuals vs plan. Spoiler: R&D came in 8% over. Worth every dollar. 🔮", "date": "March 28, 2024"},
        {"text": "All expense reports submitted on time this month. First time since I joined this team. Small wins matter. 🎉 #Finance", "date": "April 5, 2024"},
        {"text": "The new FASB guidance on cloud computing arrangements is nuanced. Spending my weekend with the standard and a highlighter. Finance is never boring. 📖", "date": "January 30, 2024"},
        {"text": "Finance team dinner last night. Turns out when you get accountants away from spreadsheets, they're actually hilarious. Who knew. 😂 #TeamCulture", "date": "February 14, 2024", "image_url": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&q=80"},
        {"text": "Automated our monthly management reporting package. Saved 14 hours per cycle. That's 168 hours per year of higher-value analysis instead of manual copy-paste. #Efficiency #Finance", "date": "March 8, 2024"},
        {"text": "Vendor payment audit complete. Found two duplicate invoices totaling $18K. That's why you audit. Every. Quarter. 🔍 #InternalControls", "date": "January 18, 2024"},
        {"text": "Year-end bonus model is done. My favorite day of the year — making the math for making people happy. 😊 #Finance", "date": "December 20, 2023"},
    ],
    "default": [
        {"text": "Great all-hands today. Leadership was transparent about the challenges AND the wins. That kind of honesty builds the trust that makes teams actually work. 🚀", "date": "April 5, 2024", "image_url": "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?w=800&q=80"},
        {"text": "Professional development day — 3 workshops, 2 new frameworks, 1 genuinely useful tool I'll use tomorrow. This is how you stay sharp. 📚", "date": "March 20, 2024"},
        {"text": "Friday wrap-up: closed 6 of 7 open items on my list. The 7th will be there Monday. Taking the win. ✨ #TGIF", "date": "March 15, 2024"},
        {"text": "Company all-hands had the highest voluntary attendance in two years. When people actually want to be there, you're doing something right. 👏", "date": "February 28, 2024"},
        {"text": "New quarter, new objectives. Spent an hour today aligning my personal goals to the company roadmap. Direction before speed. 💪 #Q2", "date": "April 1, 2024"},
        {"text": "Volunteered with the team at the regional food bank today. 200 families served. The work we do every day suddenly looks very manageable. ❤️ #CommunityImpact", "date": "March 10, 2024", "image_url": "https://images.unsplash.com/photo-1559570278-f40f9b4c4b79?w=800&q=80"},
        {"text": "Morning routine locked in: 6am walk, coffee, 20 minutes of deep reading before the first meeting. Sounds small. Has been transformative. ☕🌅 #MorningRoutine", "date": "March 4, 2024"},
        {"text": "Annual compliance training done. More interesting than expected — the social engineering module was genuinely eye-opening. Worth taking seriously. ✅", "date": "January 20, 2024"},
        {"text": "Team happy hour on the rooftop. 70 degrees, great conversations, zero work talk. This is culture. 🍻 #TeamBuilding", "date": "February 22, 2024"},
        {"text": "Reorganized my home office this weekend. New monitor arm, cable management, proper lighting. The desk you want to sit at is the desk you sit at. 🧹 #WFH", "date": "March 17, 2024", "image_url": "https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=800&q=80"},
    ],
}


def load_all_profiles():
    profiles = {}
    for f in LABS_DIR.glob("*.json"):
        with open(f, encoding="utf-8") as fh:
            lab = json.load(fh)
        company = lab["target_company"]["name"]
        industry = lab["target_company"].get("industry", "")

        # Add personas
        for pid, p in lab.get("personas", {}).items():
            slug = p["name"].lower().replace(" ", "-")
            ini = "".join(w[0].upper() for w in p["name"].split()[:2])
            posts = PERSONA_POSTS.get(pid, [])
            profiles[slug] = {
                **p,
                "slug": slug,
                "initials": ini,
                "company": company,
                "industry": industry,
                "lab_id": lab["id"],
                "persona_id": pid,
                "posts": posts,
                "is_persona": True,
            }

        # Add employees as profiles (non-persona, with generic posts)
        for emp in lab["target_company"].get("employees", []):
            slug = emp["name"].lower().replace(" ", "-")
            if slug in profiles:
                continue
            ini = "".join(w[0].upper() for w in emp["name"].split()[:2])
            role = emp.get("role", "")
            role_key = "default"
            for k in ["IT", "Marketing", "HR", "Finance"]:
                if k.lower() in role.lower():
                    role_key = k
                    break
            profiles[slug] = {
                "name": emp["name"],
                "role": role,
                "email": emp.get("email", ""),
                "phone_ext": emp.get("ext", ""),
                "slug": slug,
                "initials": ini,
                "company": company,
                "industry": industry,
                "lab_id": lab["id"],
                "persona_id": None,
                "posts": GENERIC_POSTS.get(role_key, GENERIC_POSTS["default"]),
                "is_persona": False,
                "note": emp.get("note", ""),
            }

    return profiles


PROFILES = load_all_profiles()


def avatar_gradient(name):
    h1 = int(hashlib.md5(name.encode()).hexdigest()[:6], 16) % 360
    h2 = (h1 + 35) % 360
    return f"linear-gradient(135deg, hsl({h1},60%,50%), hsl({h2},50%,38%))"


STYLE = """<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,'Segoe UI',sans-serif;background:#f3f2ef;color:#000}
.navbar{background:#fff;border-bottom:none;padding:8px 24px;display:flex;align-items:center;gap:16px;position:sticky;top:0;z-index:10;box-shadow:0 1px 0 #e0e0e0,0 2px 8px rgba(0,0,0,.06)}
.navbar .logo{font-size:22px;font-weight:800;color:#0a66c2;letter-spacing:-0.5px}
.navbar input{flex:1;max-width:320px;padding:8px 14px;border:1px solid #ddd;border-radius:6px;font-size:13px;background:#eef3f8;outline:none;transition:border-color .2s}
.navbar input:focus{border-color:#0a66c2}
.container{max-width:800px;margin:0 auto;padding:16px}
.card{background:#fff;border:1px solid #e0e0e0;border-radius:12px;margin-bottom:12px;overflow:hidden;box-shadow:0 2px 6px rgba(0,0,0,.07)}
.card-body{padding:18px 22px}
.banner{height:130px;position:relative;overflow:hidden}
.banner::after{content:'';position:absolute;inset:0;background:linear-gradient(to bottom,rgba(0,0,0,.1) 0%,rgba(0,0,0,.4) 100%);pointer-events:none}
.avatar{width:84px;height:84px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:30px;color:#fff;font-weight:700;margin-top:-42px;position:relative;border:3px solid #fff;box-shadow:0 4px 12px rgba(0,0,0,.22)}
.name{font-size:22px;font-weight:700;margin-top:10px}
.headline{font-size:14px;color:#444;margin-top:3px;font-weight:500}
.location{font-size:13px;color:#999;margin-top:3px}
.detail{font-size:12px;color:#666;margin-top:4px}
.stat-row{display:flex;gap:16px;margin-top:14px;padding-top:12px;border-top:1px solid #eee}
.stat{display:flex;flex-direction:column}
.stat-val{font-size:14px;font-weight:700;color:#0a66c2}
.stat-lbl{font-size:11px;color:#999;margin-top:1px}
.company-chip{display:inline-flex;align-items:center;gap:6px;background:#eef3f8;border:1px solid #d0dce8;border-radius:20px;padding:4px 12px 4px 6px;font-size:12px;color:#0a66c2;font-weight:600;margin-top:8px;text-decoration:none}
.company-chip-logo{width:20px;height:20px;border-radius:4px;background:#0a66c2;display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:800;color:#fff}
.section-title{font-size:16px;font-weight:700;margin-bottom:12px;padding-bottom:8px;border-bottom:2px solid #eee}
.post{border-top:1px solid #f0f0f0;padding:14px 0}
.post-text{font-size:13px;line-height:1.6;color:#333}
.post-date{font-size:11px;color:#999;margin-top:6px}
.post-likes{font-size:11px;color:#0a66c2;margin-top:4px}
.post-engage{display:flex;gap:16px;margin-top:10px;padding-top:8px;border-top:1px solid #f0f0f0}
.post-engage-btn{display:flex;align-items:center;gap:4px;font-size:12px;color:#666;cursor:pointer;padding:4px 8px;border-radius:4px;transition:background .15s;user-select:none}
.post-engage-btn:hover{background:#f3f2ef;color:#0a66c2}
.badge-photo{background:#ffe;border:1px solid #ddd;border-radius:6px;padding:8px 10px;font-size:11px;color:#666;margin-top:8px}
.search-result{padding:14px 18px;border-bottom:1px solid #eee;display:flex;gap:14px;align-items:center;cursor:pointer;text-decoration:none;color:#000;transition:background .15s,box-shadow .15s;border-radius:0}
.search-result:hover{background:#f0f6ff;box-shadow:inset 3px 0 0 #0a66c2}
.sr-avatar-wrap{width:48px;height:48px;border-radius:50%;flex-shrink:0;position:relative}
.sr-avatar-wrap img{width:48px;height:48px;border-radius:50%;object-fit:cover}
.sr-avatar{width:48px;height:48px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:17px;flex-shrink:0;box-shadow:0 2px 6px rgba(0,0,0,.12)}
.sr-name{font-size:15px;font-weight:600}
.sr-role{font-size:12px;color:#444;font-weight:500;margin-top:1px}
.sr-company{font-size:11px;background:#eef3f8;color:#0a66c2;display:inline-block;padding:2px 8px;border-radius:10px;margin-top:3px;font-weight:600}
a{color:#0a66c2;text-decoration:none}
a:hover{text-decoration:underline}
.connect-btn{background:#0a66c2;color:#fff;border:none;border-radius:20px;padding:6px 16px;font-size:12px;font-weight:600;cursor:pointer}
.connect-btn:hover{background:#004182}
.skills-tag{display:inline-block;background:#eef3f8;color:#0a66c2;padding:3px 10px;border-radius:12px;font-size:11px;margin:3px 3px 3px 0}
.dm-item:hover{background:#f3f2ef !important}
.msg-layout{display:flex;height:calc(100vh - 52px);overflow:hidden}
.msg-left{width:340px;min-width:240px;border-right:1px solid #e0e0e0;display:flex;flex-direction:column;background:#fff;overflow:hidden}
.msg-right{flex:1;display:flex;flex-direction:column;background:#fff;overflow:hidden;min-width:0}
</style>"""


def banner_gradient(name):
    h1 = int(hashlib.md5(name.encode()).hexdigest()[:6], 16) % 360
    h2 = (h1 + 60) % 360
    return f"linear-gradient(135deg, hsl({h1},60%,35%), hsl({h2},40%,25%))"


BANNER_IMGS = {
    "mgm_breach": "https://images.unsplash.com/photo-1605833556294-ea5c22a0aaec?w=1200&q=70",
    "mini_pretexting": "https://images.unsplash.com/photo-1497366754035-3ca5e7c3ad0b?w=1200&q=70",
    "mini_phishing": "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=1200&q=70",
    "chain_of_trust": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&q=70",
    "mini_tailgating": "https://images.unsplash.com/photo-1579532537598-459ecdaf39cc?w=1200&q=70",
    "mini_authority": "https://images.unsplash.com/photo-1535957998253-26ae1ef29506?w=1200&q=70",
    "mini_smishing": "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=1200&q=70",
    "mini_spear_phishing": "https://images.unsplash.com/photo-1551076805-e1869033e561?w=1200&q=70",
    "mini_quid_pro_quo": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=1200&q=70",
    "human_chain": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&q=70",
}


@app.get("/", response_class=HTMLResponse)
async def homepage():
    cards = ""
    for slug, p in sorted(PROFILES.items(), key=lambda x: x[1]["name"]):
        grad = avatar_gradient(p["name"])
        cards += f"""<a href="/profile/{slug}" class="search-result">
            <div class="sr-avatar-wrap">
              <img src="/photos/{p['name']}.png"
                   onerror="this.style.display='none';this.nextElementSibling.style.display='flex'"
                   style="width:48px;height:48px;border-radius:50%;object-fit:cover;">
              <div class="sr-avatar" style="display:none;background:{grad};position:absolute;top:0;left:0">{p['initials']}</div>
            </div>
            <div style="min-width:0">
                <div class="sr-name">{p['name']}</div>
                <div class="sr-role">{p['role']}</div>
                <div class="sr-company">{p['company']}</div>
            </div>
        </a>"""

    return f"""<!DOCTYPE html><html><head><title>LinkHub — Professional Network</title>{STYLE}</head><body>
<div class="navbar">
    <a href="/" class="logo" style="text-decoration:none">Link<span style="color:#000">Hub</span></a>
    <input placeholder="Search people, companies..." id="search" oninput="filterProfiles(this.value)">
    <span style="font-size:12px;color:#666">{len(PROFILES)} members</span>
    <a href="/login" style="margin-left:auto;background:#0a66c2;color:#fff;padding:7px 18px;border-radius:20px;font-size:13px;font-weight:600;text-decoration:none">Login</a>
</div>
<div class="container">
    <div class="card">
        <div class="card-body" style="padding:8px 0">
            <div id="profiles">{cards}</div>
        </div>
    </div>
</div>
<script>
function filterProfiles(q) {{
    const items = document.querySelectorAll('.search-result');
    q = q.toLowerCase();
    items.forEach(el => {{
        const text = el.textContent.toLowerCase();
        el.style.display = text.includes(q) ? 'flex' : 'none';
    }});
}}
</script>
</body></html>"""


@app.get("/profile/{slug}", response_class=HTMLResponse)
async def profile(slug: str, request: Request):
    p = PROFILES.get(slug)
    if not p:
        return HTMLResponse("<h1>Profile not found</h1>", status_code=404)

    user_id = request.query_params.get("user_id", "")
    lab_id = p.get("lab_id", "")
    persona_id = p.get("persona_id", "")

    grad = avatar_gradient(p["name"])
    bg = banner_gradient(p["name"])
    banner_img = BANNER_IMGS.get(lab_id, "")
    banner_photo_html = f'<img src="{banner_img}" style="position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;opacity:0.6" loading="lazy">' if banner_img else ""
    social = p.get("social_media", {})
    bio = social.get("linkedin_bio", "")
    if not bio:
        import re as _re
        role_short = _re.sub(r'\s+at\s+\S.*$', '', p['role'], flags=_re.IGNORECASE).strip()
        bio = f"{role_short} at {p['company']}. Passionate about making an impact."
    posts_data = p.get("posts", [])

    import hashlib as _hl
    posts_html = ""
    for post in posts_data:
        text = post if isinstance(post, str) else post.get("text", "")
        date = post.get("date", "Recent") if isinstance(post, dict) else "Recent"
        likes = post.get("likes", "") if isinstance(post, dict) else ""
        badge = ""
        if isinstance(post, dict) and post.get("badge_photo"):
            badge = '<div class="badge-photo">📸 [Photo: Employee badge visible — ID partially readable: GM-2024-08**]</div>'
        img_html = ""
        if isinstance(post, dict) and post.get("image_url"):
            img_html = f'<img src="{post["image_url"]}" style="width:100%;border-radius:8px;margin-top:10px;max-height:320px;object-fit:cover;display:block;" loading="lazy">'
        ph = int(_hl.md5(f"{p['name']}{date}".encode()).hexdigest(), 16)
        _pl = likes if likes else 3 + (ph % 40)
        _pc = 1 + (ph >> 4) % 12
        _pr = (ph >> 8) % 8
        engage_html = (
            f'<div class="post-engage">'
            f'<button class="post-engage-btn">👍 {_pl}</button>'
            f'<button class="post-engage-btn">💬 {_pc}</button>'
            f'<button class="post-engage-btn">🔁 {_pr}</button>'
            f'<button class="post-engage-btn" style="margin-left:auto">✈️ Send</button>'
            f'</div>'
        )
        posts_html += f"""<div class="post">
            <div class="post-text">{text}</div>
            {img_html}
            <div class="post-date">{date}</div>
            {badge}
            {engage_html}
        </div>"""

    # Details for OSINT
    details = []
    if p.get("age"):
        details.append(f"📅 Age: {p['age']}")
    if p.get("email"):
        details.append(f"📧 {p['email']}")
    if p.get("phone_ext"):
        details.append(f"📞 Office ext: {p['phone_ext']}")
    if p.get("note"):
        details.append(f"📝 {p['note']}")

    details_html = "".join(f'<div class="detail" style="margin-top:4px">{d}</div>' for d in details)

    _h = int(_hl.md5(p['name'].encode()).hexdigest(), 16)
    _conn = 200 + (_h % 600)
    conn_label = "500+" if _conn >= 500 else str(_conn)
    follower_count = _conn + ((_h >> 8) % 200)
    stat_row_html = (
        f'<div class="stat-row">'
        f'<div class="stat"><span class="stat-val">{conn_label}</span><span class="stat-lbl">connections</span></div>'
        f'<div class="stat"><span class="stat-val">{follower_count}</span><span class="stat-lbl">followers</span></div>'
        f'</div>'
    )

    company_chip_html = (
        f'<a href="#" class="company-chip" style="text-decoration:none">'
        f'<div class="company-chip-logo">{p["company"][0]}</div>'
        f'{_he(p["company"])}</a>'
    )

    # Skills tags — ordered most-specific first to avoid substring false-matches
    import re as _re
    rl = p["role"].lower()
    if _re.search(r'\b(ceo|chief executive|founder|managing partner|managing director|general partner)\b', rl):
        skills = ["Leadership", "M&A", "Capital Allocation", "Investor Relations", "Strategy", "Board Governance"]
    elif _re.search(r'\b(cfo|chief financial officer|vp finance|finance director|treasurer)\b', rl):
        skills = ["Financial Strategy", "Treasury", "Fund Operations", "Risk Management", "Audit", "Controls"]
    elif _re.search(r'\b(cso|ciso|chief security|security director|security officer|security engineer)\b', rl):
        skills = ["Threat Intelligence", "Penetration Testing", "OSINT", "Incident Response", "SIEM", "Zero Trust"]
    elif _re.search(r'\b(executive assistant|ea)\b', rl):
        skills = ["Executive Support", "Calendar Management", "Event Coordination", "Travel Logistics", "Stakeholder Relations", "Communications"]
    elif _re.search(r'\b(principal|superintendent|dean)\b', rl):
        skills = ["Educational Leadership", "Curriculum", "Staff Development", "Community Relations", "Policy", "Accreditation"]
    elif _re.search(r'\b(help.?desk|it support|sysadmin|it admin|it manager|it lead|it director)\b', rl):
        skills = ["IT Support", "ServiceNow", "Active Directory", "Troubleshooting", "Windows", "Networking"]
    elif "market" in rl:
        skills = ["Digital Marketing", "Brand Strategy", "Analytics", "Content", "Social Media", "SEO"]
    elif "account" in rl or "financ" in rl or "audit" in rl:
        skills = ["Financial Analysis", "Excel", "Auditing", "GAAP", "Reporting", "Budgeting"]
    elif "devops" in rl or "sre" in rl or "infrastructure" in rl or "platform" in rl:
        skills = ["Kubernetes", "Terraform", "AWS", "CI/CD", "SRE", "Docker"]
    elif "develop" in rl or "engineer" in rl or "software" in rl or "backend" in rl or "frontend" in rl:
        skills = ["Python", "JavaScript", "AWS", "Docker", "Git", "Agile"]
    elif "data" in rl or "analyst" in rl or "scientist" in rl:
        skills = ["Python", "SQL", "Data Analysis", "Pandas", "Visualization", "Statistics"]
    elif "teacher" in rl or "educat" in rl or "instructor" in rl or "professor" in rl:
        skills = ["Curriculum Design", "Classroom Management", "EdTech", "Assessment", "Mentoring"]
    elif "product" in rl:
        skills = ["Product Strategy", "Agile", "User Research", "Roadmapping", "A/B Testing", "Analytics"]
    elif "hr" in rl or "human resource" in rl or "people ops" in rl or "talent" in rl or "recruiting" in rl:
        skills = ["Talent Acquisition", "Performance Management", "Culture", "HRIS", "Benefits", "Onboarding"]
    elif "game" in rl or "design" in rl or "creative" in rl or "ux" in rl:
        skills = ["Game Design", "Unity", "Narrative Design", "Level Design", "UX", "Prototyping"]
    else:
        skills = ["Leadership", "Communication", "Project Management", "Strategy"]

    skills_html = "".join(f'<span class="skills-tag">{s}</span>' for s in skills)

    # DM panel HTML (only shown for contactable personas)
    dm_panel_html = ""
    dm_button_html = ""
    if p.get("is_persona") and persona_id:
        dm_button_html = f'<button class="connect-btn" onclick="openDm()" style="background:#fff;color:#0a66c2;border:1px solid #0a66c2;margin-left:8px">Message</button>'
        dm_panel_html = f"""<!-- DM Panel -->
<div id="dm-panel" style="display:none;position:fixed;bottom:20px;right:20px;width:340px;background:#fff;border:1px solid #ddd;border-radius:12px;box-shadow:0 4px 24px rgba(0,0,0,0.15);z-index:100;font-family:-apple-system,'Segoe UI',sans-serif;">
  <div style="padding:12px 16px;border-bottom:1px solid #eee;display:flex;justify-content:space-between;align-items:center">
    <div>
      <div style="font-size:14px;font-weight:700">{p['name']}</div>
      <div style="font-size:11px;color:#666">{p['role']}</div>
    </div>
    <button onclick="document.getElementById('dm-panel').style.display='none'" style="background:none;border:none;cursor:pointer;font-size:18px;color:#999">&#x2715;</button>
  </div>
  <div id="dm-messages" style="height:200px;overflow-y:auto;padding:12px;display:flex;flex-direction:column;gap:8px;"></div>
  <div style="padding:10px;border-top:1px solid #eee;display:flex;gap:8px">
    <input id="dm-input" placeholder="Write a message..." style="flex:1;padding:8px 12px;border:1px solid #ddd;border-radius:20px;font-size:13px;outline:none" onkeydown="if(event.key==='Enter')sendDm()">
    <button onclick="sendDm()" style="background:#0a66c2;color:#fff;border:none;border-radius:50%;width:36px;height:36px;cursor:pointer;font-size:16px">&#x27A4;</button>
  </div>
</div>

<script>
var DM_PERSONA_ID = "{persona_id}";
var DM_LAB_ID = "{lab_id}";
var DM_USER_ID = new URLSearchParams(window.location.search).get('user_id') || '{user_id}';
var DM_LOGGED_IN_PERSONA_ID = sessionStorage.getItem('linkhub_persona_id') || '';

function openDm() {{
  document.getElementById('dm-panel').style.display = 'block';
}}

function addMessage(text, isMe) {{
  var msgs = document.getElementById('dm-messages');
  var div = document.createElement('div');
  div.style.cssText = 'display:flex;justify-content:' + (isMe ? 'flex-end' : 'flex-start');
  div.innerHTML = '<div style="max-width:75%;padding:8px 12px;border-radius:' + (isMe ? '16px 16px 4px 16px' : '16px 16px 16px 4px') + ';background:' + (isMe ? '#0a66c2' : '#f0f0f0') + ';color:' + (isMe ? '#fff' : '#000') + ';font-size:13px;line-height:1.4;white-space:pre-wrap">' + text.replace(/</g,'&lt;').replace(/>/g,'&gt;') + '</div>';
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
}}

function addTyping() {{
  var msgs = document.getElementById('dm-messages');
  var div = document.createElement('div');
  div.id = 'typing-indicator';
  div.innerHTML = '<div style="background:#f0f0f0;padding:8px 12px;border-radius:16px;font-size:13px;color:#999">typing...</div>';
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
}}

function removeTyping() {{
  var el = document.getElementById('typing-indicator');
  if (el) el.remove();
}}

function sendDm() {{
  var input = document.getElementById('dm-input');
  var msg = input.value.trim();
  if (!msg) return;
  input.value = '';
  addMessage(msg, true);
  addTyping();

  fetch('/api/dm/send', {{
    method: 'POST',
    headers: {{'Content-Type':'application/json'}},
    body: JSON.stringify({{
      user_id: DM_USER_ID,
      lab_id: DM_LAB_ID,
      persona_id: DM_PERSONA_ID,
      message: msg,
      logged_in_persona_id: DM_LOGGED_IN_PERSONA_ID
    }})
  }})
  .then(r => r.json())
  .then(data => {{
    removeTyping();
    if (data.reply) addMessage(data.reply, false);
    else if (data.error) addMessage('[Error: ' + data.error + ']', false);
  }})
  .catch(() => {{ removeTyping(); addMessage('[Connection error]', false); }});
}}
</script>"""

    return f"""<!DOCTYPE html><html><head><title>{p['name']} — LinkHub</title>{STYLE}</head><body>
<div class="navbar">
    <a href="/" class="logo" style="text-decoration:none">Link<span style="color:#000">Hub</span></a>
    <input placeholder="Search people, companies...">
</div>
<div class="container">
    <div class="card">
        <div class="banner" style="background:{bg}">{banner_photo_html}</div>
        <div class="card-body">
            <div style="position:relative;width:84px;height:84px;margin-top:-42px">
              <img src="/photos/{p['name']}.png"
                   onerror="this.style.display='none';this.nextElementSibling.style.display='flex'"
                   style="width:84px;height:84px;border-radius:50%;object-fit:cover;border:4px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,.15);">
              <div style="display:none;width:84px;height:84px;border-radius:50%;background:{grad};align-items:center;justify-content:center;font-size:30px;font-weight:700;color:white;position:absolute;top:0;left:0;border:4px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,.15)">
                {p['initials']}
              </div>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div>
                    <div class="name">{p['name']}</div>
                    <div class="headline">{p['role']}</div>
                    <div class="location">{p.get('industry','') if p.get('industry') else ''}</div>
                    {company_chip_html}
                </div>
                <div style="display:flex;align-items:center;margin-top:12px">
                    <button class="connect-btn">+ Connect</button>
                    {dm_button_html}
                </div>
            </div>
            <p style="margin-top:12px;font-size:13px;color:#333;line-height:1.6">{bio}</p>
            <div style="margin-top:8px">{details_html}</div>
            {stat_row_html}
        </div>
    </div>

    <div class="card">
        <div class="card-body">
            <div class="section-title">Skills</div>
            <div>{skills_html}</div>
        </div>
    </div>

    <div class="card">
        <div class="card-body">
            <div class="section-title">Activity — {len(posts_data)} posts</div>
            {posts_html}
        </div>
    </div>

    <div class="card">
        <div class="card-body">
            <div class="section-title">Experience</div>
            <div style="display:flex;gap:12px;align-items:flex-start">
                <div style="width:40px;height:40px;border-radius:6px;background:#eef3f8;display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:700;color:#0a66c2;flex-shrink:0">
                    {p['company'][0]}
                </div>
                <div>
                    <p style="font-size:14px;font-weight:600">{p['role']}</p>
                    <p style="font-size:13px;color:#666">{p['company']}</p>
                    <p style="font-size:12px;color:#999">Present</p>
                </div>
            </div>
        </div>
    </div>
</div>
{dm_panel_html}
<!-- OSINT data embedded in profiles for CTF reconnaissance -->
</body></html>"""


NPC_CREDENTIALS = {
    # email → {slug, name, password, persona_id, lab_id}
    # mgm_breach
    "elena.rodriguez@goldenmirage.com": {"slug": "elena-rodriguez", "name": "Elena Rodriguez", "password": "Helpdesk#2020", "persona_id": "elena_helpdesk", "lab_id": "mgm_breach"},
    "marcus.chen@goldenmirage.com":     {"slug": "marcus-chen",     "name": "Marcus Chen",     "password": "Biscuit#23",    "persona_id": "marcus_linkedin", "lab_id": "mgm_breach"},
    "sarah.mitchell@goldenmirage.com":  {"slug": "sarah-mitchell",  "name": "Sarah Mitchell",  "password": "Marketing5yr!", "persona_id": "sarah_manager",   "lab_id": "mgm_breach"},
    # human_chain
    "ben.morgan@meridiancap.com":       {"slug": "ben-morgan",      "name": "Ben Morgan",      "password": "Office8332!",   "persona_id": "ben_morgan",      "lab_id": "human_chain"},
    "rachel.park@meridiancap.com":      {"slug": "rachel-park",     "name": "Rachel Park",     "password": "EA_Rachel5!",   "persona_id": "rachel_park",     "lab_id": "human_chain"},
    "james.cole@meridiancap.com":       {"slug": "james-cole",      "name": "James Cole",      "password": "Finance@2200",  "persona_id": "james_cole",      "lab_id": "human_chain"},
    "sarah.whitfield@meridiancap.com":  {"slug": "sarah-whitfield", "name": "Sarah Whitfield", "password": "CFO#Meridian1", "persona_id": "sarah_whitfield", "lab_id": "human_chain"},
    "alex.reed@meridiancap.com":        {"slug": "alex-reed",       "name": "Alex Reed",       "password": "SecOps@MC24",   "persona_id": "alex_reed",       "lab_id": "human_chain"},
    # mini_quid_pro_quo
    "sandra.williams@brightpath.com":   {"slug": "sandra-williams", "name": "Sandra Williams", "password": "Teacher24!",    "persona_id": "sandra_teacher",       "lab_id": "mini_quid_pro_quo"},
    "margaret.hayes@brightpath.com":    {"slug": "principal-margaret-hayes", "name": "Principal Margaret Hayes", "password": "BrightPath30!", "persona_id": "principal_margaret_hayes", "lab_id": "mini_quid_pro_quo"},
    "john.carter@brightpath.com":       {"slug": "john-carter",     "name": "John Carter",     "password": "IT@Bright6050", "persona_id": "john_carter",     "lab_id": "mini_quid_pro_quo"},
    "emily.foster@brightpath.com":      {"slug": "dr.-emily-foster","name": "Dr. Emily Foster","password": "Chem_Foster24", "persona_id": "emily_foster",    "lab_id": "mini_quid_pro_quo"},
    "carlos.rivera@brightpath.com":     {"slug": "carlos-rivera",   "name": "Carlos Rivera",   "password": "MathTeam10!",   "persona_id": "carlos_rivera",   "lab_id": "mini_quid_pro_quo"},
    # mini_smishing
    "david.liu@novapay.com":            {"slug": "david-liu",       "name": "David Liu",       "password": "NovaPay#Liu",   "persona_id": "david_target",    "lab_id": "mini_smishing"},
    "tina.zhao@novapay.com":            {"slug": "tina-zhao",       "name": "Tina Zhao",       "password": "NovaPay#Tina",  "persona_id": "tina_zhao",       "lab_id": "mini_smishing"},
    "kevin.brooks@novapay.com":         {"slug": "kevin-brooks",    "name": "Kevin Brooks",    "password": "NovaPay#KB",    "persona_id": "kevin_brooks",    "lab_id": "mini_smishing"},
    "sarah.lee@novapay.com":            {"slug": "sarah-lee",       "name": "Sarah Lee",       "password": "NovaPay#SL24",  "persona_id": "sarah_lee",       "lab_id": "mini_smishing"},
    "omar.hassan@novapay.com":          {"slug": "omar-hassan",     "name": "Omar Hassan",     "password": "NovaPay#OH24",  "persona_id": "omar_hassan",     "lab_id": "mini_smishing"},
    # mini_authority
    "priya.sharma@greenleaf.com":       {"slug": "priya-sharma",    "name": "Priya Sharma",    "password": "GreenLeaf#PS",  "persona_id": "priya_analyst",   "lab_id": "mini_authority"},
    "robert.chen@greenleaf.com":        {"slug": "robert-chen",     "name": "Robert Chen",     "password": "GreenLeaf#RC",  "persona_id": "robert_chen",     "lab_id": "mini_authority"},
    "linda.hayes@greenleaf.com":        {"slug": "linda-hayes",     "name": "Linda Hayes",     "password": "GreenLeaf#LH",  "persona_id": "linda_hayes",     "lab_id": "mini_authority"},
    "mark.wilson@greenleaf.com":        {"slug": "mark-wilson",     "name": "Mark Wilson",     "password": "GreenLeaf#MW",  "persona_id": "mark_wilson",     "lab_id": "mini_authority"},
    "susan.bell@greenleaf.com":         {"slug": "susan-bell",      "name": "Susan Bell",      "password": "GreenLeaf#SB8", "persona_id": "susan_bell",      "lab_id": "mini_authority"},
    # chain_of_trust
    "a.reeves@helixsystems.io":         {"slug": "alicia-reeves",   "name": "Alicia Reeves",   "password": "Helix_AR2024",  "persona_id": "carol_mitchell",  "lab_id": "chain_of_trust"},
    "r.nguyen@helixsystems.io":         {"slug": "rachel-nguyen",   "name": "Rachel Nguyen",   "password": "Helix_RN2024",  "persona_id": "chris_park",      "lab_id": "chain_of_trust"},
    "j.whitfield@helixsystems.io":      {"slug": "dr.-james-whitfield","name": "Dr. James Whitfield","password": "Helix_JW2024","persona_id": "robert_torres","lab_id": "chain_of_trust"},
    "s.cole@helixsystems.io":           {"slug": "stephanie-cole",  "name": "Stephanie Cole",  "password": "Helix_SC2024",  "persona_id": "lisa_harmon",     "lab_id": "chain_of_trust"},
    "y.tanaka@helixsystems.io":         {"slug": "yuki-tanaka",     "name": "Yuki Tanaka",     "password": "Helix_YT2024",  "persona_id": "mike_donahue",    "lab_id": "chain_of_trust"},
}

NPC_INBOX = {
    "elena-rodriguez": [
        {"from": "David Park", "from_email": "d.park@goldenmirage.com", "date": "Apr 9, 2024 14:23",
         "subject": "VPN Admin Creds — CONFIDENTIAL",
         "body": "Elena,\n\nFor the Okta admin console: admin account is OktaAdmin, password GM_Okta#2024. We're rotating next Friday — remind me.\n\nAlso the ServiceNow admin token: SN_TOKEN_GM_2024_PROD. Only use in emergencies.\n\n— David"},
        {"from": "Sarah Mitchell", "from_email": "sarah.mitchell@goldenmirage.com", "date": "Apr 1, 2024 09:11",
         "subject": "Re: Marcus Chen onboarding",
         "body": "Elena,\n\nCan you make sure Marcus gets access to the Salesforce Marketing Cloud? His employee ID is EMP-4421 and his temp domain password should be Welcome@GM2024.\n\nHe starts today. Thanks!\n— Sarah"},
        {"from": "Marcus Chen", "from_email": "marcus.chen@goldenmirage.com", "date": "Apr 2, 2024 16:45",
         "subject": "Password reset request",
         "body": "Hi Elena,\n\nI forgot my temp password already 😅. Could you reset it? My verification code from the SMS is 8874.\n\nThanks so much!\nMarcus"},
    ],
    "marcus-chen": [
        {"from": "IT Onboarding", "from_email": "it-noreply@goldenmirage.com", "date": "Apr 1, 2024 08:00",
         "subject": "Welcome to Golden Mirage — Your IT Credentials",
         "body": "Hi Marcus,\n\nWelcome! Your temporary credentials:\n• Domain login: marcus.chen@goldenmirage.com\n• Temp password: Welcome@GM2024 (change within 24h)\n• VPN: gm-vpn.goldenmirage.com — use your domain creds\n• ServiceNow: same credentials\n\nEmployee ID: EMP-4421\n\nIT Help Desk — ext. 1000"},
        {"from": "Sarah Mitchell", "from_email": "sarah.mitchell@goldenmirage.com", "date": "Apr 1, 2024 10:30",
         "subject": "Salesforce Marketing Cloud access",
         "body": "Marcus,\n\nYour Salesforce access: https://goldenmirage.my.salesforce.com\nUsername: marcus.chen@goldenmirage.com\nTeam token: MKT-SFDC-GM-2024\n\nLet me know if you have any issues!\n— Sarah"},
    ],
    "sarah-mitchell": [
        {"from": "Richard Blackwell (CEO)", "from_email": "r.blackwell@goldenmirage.com", "date": "Apr 3, 2024 18:00",
         "subject": "Q2 Campaign Budget — For Your Eyes Only",
         "body": "Sarah,\n\nQ2 campaign approval code: CAMP-2024-Q2-AUTH. Budget approved: $2.4M.\n\nThe loyalty program expansion details are in the shared drive under /Confidential/Q2-2024/. Password: GM_Exec2024.\n\n— Richard"},
        {"from": "Elena Rodriguez", "from_email": "elena.rodriguez@goldenmirage.com", "date": "Apr 5, 2024 11:20",
         "subject": "Marketing team VPN renewal",
         "body": "Hi Sarah,\n\nMarketing team VPN group credentials renewed:\n• Group: marketing-gm\n• Password: GMMkt#April24\n\nAll team members need to update their VPN config by Friday.\n\n— Elena, IT Help Desk"},
    ],
    "ben-morgan": [
        {"from": "Rachel Park", "from_email": "rachel.park@meridiancap.com", "date": "Apr 9, 2024 07:30",
         "subject": "Today's schedule + Lighthouse closing",
         "body": "Ben,\n\nYour day:\n09:00 — Lighthouse escrow call\n11:00 — Bloomberg prep\n14:00 — Bloomberg interview (live)\n16:30 — LP call\n\nLighthouse wire auth code (James needs this): WIRE-AUTH-2024-LH-MC\nAmount: $2.1M to escrow account 4421-MC-ESCROW\n\n— Rachel"},
        {"from": "Alex Reed", "from_email": "alex.reed@meridiancap.com", "date": "Apr 8, 2024 17:00",
         "subject": "Security briefing follow-up",
         "body": "Ben,\n\nFollowing today's deepfake briefing — our verification word for out-of-band wire requests is: IRONMAN.\n\nIf anyone calls claiming to be you requesting a wire, James should ask for this word. Non-negotiable.\n— Alex"},
    ],
    "rachel-park": [
        {"from": "Ben Morgan", "from_email": "ben.morgan@meridiancap.com", "date": "Apr 9, 2024 06:15",
         "subject": "Lighthouse — urgent wire today",
         "body": "Rachel,\n\nLighthouse closes today. Need James to process $2.1M wire to escrow account 4421-MC-ESCROW.\n\nAuth code: WIRE-AUTH-2024-LH-MC\n\nCoordinate with him directly — I'll be on Bloomberg set.\n— Ben"},
        {"from": "James Cole", "from_email": "james.cole@meridiancap.com", "date": "Apr 9, 2024 09:45",
         "subject": "Re: Lighthouse wire",
         "body": "Rachel,\n\nWire is staged but I need Sarah Whitfield's dual approval before it goes. Policy is policy, even for Ben.\n\nHer extension is 3100. Please escalate to her.\n— James"},
    ],
    "james-cole": [
        {"from": "Rachel Park", "from_email": "rachel.park@meridiancap.com", "date": "Apr 9, 2024 09:00",
         "subject": "Wire authorization — Lighthouse closing",
         "body": "James,\n\nBen approved the Lighthouse wire. Details:\n• Amount: $2.1M\n• Account: 4421-MC-ESCROW\n• Auth code: WIRE-AUTH-2024-LH-MC\n\nPlease process today.\n— Rachel"},
        {"from": "Sarah Whitfield", "from_email": "sarah.whitfield@meridiancap.com", "date": "Apr 9, 2024 10:00",
         "subject": "Do NOT process that wire",
         "body": "James,\n\nDo not process any wire without my verbal confirmation at ext. 3100. Period. I haven't approved this.\n\nWe had a deepfake vishing attempt last month — this looks identical. Call me.\n— Sarah"},
    ],
    "sarah-whitfield": [
        {"from": "Alex Reed", "from_email": "alex.reed@meridiancap.com", "date": "Apr 9, 2024 08:30",
         "subject": "ALERT: Possible deepfake vishing in progress",
         "body": "Sarah,\n\nOur phone system flagged an inbound call to Rachel claiming to be Ben — voice analysis shows 94% match to a synthetic model, not Ben's actual voice.\n\nThey're targeting the Lighthouse wire. I've alerted James. Please call him on ext. 2200 immediately.\n— Alex"},
    ],
    "john-carter": [
        {"from": "Principal Margaret Hayes", "from_email": "margaret.hayes@brightpath.com", "date": "Apr 12, 2024 10:00",
         "subject": "Software install request — urgent",
         "body": "John,\n\nEmily Foster needs an educational analytics tool installed on her classroom PC. The vendor says it requires admin install. Can you assist today?\n\nAdmin install code for approved apps: BPATH-ADMIN-2024\nEmily's device ID: BP-PC-0042\n\nThanks\n— Margaret"},
        {"from": "Helpdesk System", "from_email": "helpdesk@brightpath.com", "date": "Apr 10, 2024 09:00",
         "subject": "Daily digest — open tickets",
         "body": "Open tickets:\n• BP-1247: Sandra Williams — M365 password reset (ext. 4412)\n• BP-1248: Carlos Rivera — Calculator app license\n• BP-1249: Emily Foster — Pending admin software install\n\nHelpdesk portal: help.brightpath.com\nAdmin: john.carter@brightpath.com / IT@Bright6050"},
    ],
    "sandra-williams": [
        {"from": "John Carter", "from_email": "john.carter@brightpath.com", "date": "Apr 11, 2024 14:00",
         "subject": "Re: M365 login issue",
         "body": "Sandra,\n\nI've reset your Microsoft 365 password. Temp credentials:\n• Username: s.williams@brightpath.com\n• Temp password: BrightPath2024\n• Change required on next login\n\nAlso: the analytics tool you wanted — I need admin approval (Principal Hayes) before installing. Can you get her sign-off?\n— John"},
        {"from": "Unknown Sender", "from_email": "support@microsoftsecure-365.com", "date": "Apr 12, 2024 08:00",
         "subject": "⚠️ Microsoft 365 Security Alert — Action Required",
         "body": "Your Microsoft 365 account requires immediate verification.\n\nClick here to verify: http://microsoftsecure-365.com/verify\n\nThis is a phishing simulation. If you see this in your real inbox — report to John Carter ext. 6050 immediately."},
    ],
    "david-liu": [
        {"from": "NovaPay Security", "from_email": "security@novapay.com", "date": "Apr 14, 2024 11:00",
         "subject": "Account security notice",
         "body": "David,\n\nYour NovaPay account was accessed from an unrecognized device.\n\nVerification code: NP-7891-DL\nThis code expires in 10 minutes.\n\nIf this wasn't you, call security immediately at ext. 9001."},
        {"from": "Tina Zhao", "from_email": "tina.zhao@novapay.com", "date": "Apr 13, 2024 15:30",
         "subject": "Q2 Settlement code",
         "body": "David,\n\nThe mobile payment verification code for the Q2 settlement batch is: 8847. Expires end of month.\n\nDon't share — Kevin already has his own.\n— Tina"},
    ],
    "priya-sharma": [
        {"from": "Mark Wilson", "from_email": "mark.wilson@greenleaf.com", "date": "Apr 9, 2024 09:00",
         "subject": "Q3 Research data access",
         "body": "Priya,\n\nQ3 research data access key: GL-DATA-Q3-2024\nGenomic database updated password: GL_Genome#2024\n\nReminder: all external data sharing requires Dr. Chen's sign-off.\n— Mark"},
        {"from": "Dr. Robert Chen", "from_email": "robert.chen@greenleaf.com", "date": "Apr 7, 2024 14:00",
         "subject": "Budget approval — R&D equipment",
         "body": "Priya,\n\nBudget approval code for the spectrophotometer order: RDBUD-2024-7891. Submit to finance with this code.\n\nThe Phase III data you've been working on — keep the NDA in mind. Even internal sharing needs to go through me.\n— Robert"},
    ],
    "alicia-reeves": [
        {"from": "IT Admin", "from_email": "it@helixsystems.io", "date": "Apr 5, 2024 09:00",
         "subject": "Admin credentials — Helix Systems",
         "body": "Alicia,\n\nYour Helix admin credentials:\n• Email: a.reeves@helixsystems.io\n• Password: HelixIT#2024 (please change)\n• Admin portal: admin.helixsystems.io\n• API key (production): hx-api-2024-prod-4421\n\n— IT"},
        {"from": "Rachel Nguyen", "from_email": "r.nguyen@helixsystems.io", "date": "Apr 8, 2024 16:00",
         "subject": "Customer data integration",
         "body": "Alicia,\n\nThe API key for the customer data pipeline is: hx-api-2024-prod-4421\n\nDr. Whitfield needs the genomics dataset export by Friday. Access through the secure portal only.\n— Rachel"},
    ],
}


@app.post("/api/npc-login")
async def npc_login(request: Request):
    body = await request.json()
    email = body.get("email", "").lower().strip()
    password = body.get("password", "")
    if not email or not password:
        return {"success": False, "error": "Email and password required"}
    cred = NPC_CREDENTIALS.get(email)
    if not cred:
        return {"success": False, "error": "Account not found — have you phished this target yet?"}
    if cred["password"] != password:
        return {"success": False, "error": "Invalid credentials"}
    return {"success": True, "slug": cred["slug"], "name": cred["name"], "persona_id": cred["persona_id"], "lab_id": cred["lab_id"]}


@app.get("/api/npc-inbox/{slug}")
async def npc_inbox(slug: str):
    msgs = NPC_INBOX.get(slug, [])
    return {"slug": slug, "messages": msgs}


@app.get("/api/npc-credentials-hint")
async def npc_credentials_hint(lab_id: str = ""):
    hints = []
    for email, cred in NPC_CREDENTIALS.items():
        if not lab_id or cred["lab_id"] == lab_id:
            hints.append({"email": email, "name": cred["name"], "slug": cred["slug"], "lab_id": cred["lab_id"]})
    return {"accounts": hints}


@app.post("/api/dm/send")
async def dm_send(request: Request):
    body = await request.json()
    persona_id = body.get("persona_id", "")
    lab_id = body.get("lab_id", "")
    user_id = body.get("user_id", "") or "1"
    message = body.get("message", "")

    logged_in_persona_id = body.get("logged_in_persona_id", "")

    if not persona_id or not message:
        return {"error": "Missing required fields"}

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post("http://127.0.0.1:8000/api/chat", json={
                "user_id": int(user_id) if str(user_id).isdigit() else 1,
                "lab_id": lab_id,
                "persona_id": persona_id,
                "message": message,
                "channel": "linkhub",
                "linkhub_authenticated_as": logged_in_persona_id,
            })
            data = resp.json()
            if resp.status_code == 409:
                detail = data.get("detail", {})
                if isinstance(detail, dict) and detail.get("error") == "lab_not_started":
                    return {"reply": "[Simulation not started — launch the lab from the main app first]"}
            if resp.status_code >= 400:
                return {"reply": f"[Error {resp.status_code}: {data.get('detail', data.get('message', 'Unknown error'))}]"}
            return {
                "reply": data.get("reply", data.get("response", data.get("message", ""))),
                "mission_failed": data.get("mission_failed", False),
                "flag_found": data.get("flag_found"),
            }
    except Exception as e:
        return {"error": str(e)}


@app.get("/login", response_class=HTMLResponse)
async def linkhub_login_page(lab_id: str = "", user_id: str = ""):
    return f"""<!DOCTYPE html><html><head><title>LinkHub Login</title>{STYLE}</head><body>
<div class="navbar">
    <a href="/" class="logo" style="text-decoration:none">Link<span style="color:#000">Hub</span></a>
</div>
<div class="container" style="max-width:400px;margin-top:40px">
    <div class="card">
        <div class="card-body">
            <h2 style="font-size:20px;font-weight:700;margin-bottom:6px">Sign in to LinkHub</h2>
            <p style="font-size:13px;color:#666;margin-bottom:20px">Enter your credentials to access your account</p>
            <div id="error-msg" style="display:none;color:#cc0000;font-size:13px;padding:8px;background:#fff0f0;border:1px solid #ffcccc;border-radius:6px;margin-bottom:14px"></div>
            <div style="margin-bottom:14px">
                <label style="font-size:12px;font-weight:600;color:#333">Email or Username</label>
                <input id="email" type="email" placeholder="Enter your email" style="width:100%;padding:10px 12px;border:1px solid #ddd;border-radius:6px;font-size:13px;margin-top:6px;box-sizing:border-box">
            </div>
            <div style="margin-bottom:20px">
                <label style="font-size:12px;font-weight:600;color:#333">Password</label>
                <input id="password" type="password" placeholder="Enter your password" style="width:100%;padding:10px 12px;border:1px solid #ddd;border-radius:6px;font-size:13px;margin-top:6px;box-sizing:border-box">
            </div>
            <button onclick="doLogin()" style="width:100%;padding:12px;background:#0a66c2;color:#fff;border:none;border-radius:6px;font-size:14px;font-weight:600;cursor:pointer">Sign In</button>
        </div>
    </div>
</div>
<script>
var LAB_ID = "{lab_id}";
var USER_ID = "{user_id}";
function doLogin() {{
    var email = document.getElementById('email').value;
    var password = document.getElementById('password').value;
    if (!email || !password) {{ showError('Please enter email and password'); return; }}
    fetch('/api/npc-login', {{
        method: 'POST',
        headers: {{'Content-Type':'application/json'}},
        body: JSON.stringify({{email: email, password: password}})
    }})
    .then(r => r.json())
    .then(data => {{
        if (data.success) {{
            sessionStorage.setItem('linkhub_persona_id', data.persona_id || '');
            window.location.href = '/inbox?as=' + data.slug + '&lab_id=' + (LAB_ID || data.lab_id) + '&user_id=' + USER_ID;
        }} else {{
            showError(data.error || 'Invalid credentials — have you harvested this account yet?');
        }}
    }})
    .catch(() => showError('Connection error'));
}}
function showError(msg) {{
    var el = document.getElementById('error-msg');
    el.textContent = msg; el.style.display = 'block';
}}
document.addEventListener('keydown', e => {{ if(e.key==='Enter') doLogin(); }});
</script>
</body></html>"""


@app.get("/inbox", response_class=HTMLResponse)
async def linkhub_inbox(request: Request):
    as_param = request.query_params.get("as", "")
    lab_id = request.query_params.get("lab_id", "")
    user_id = request.query_params.get("user_id", "")

    profile_data = PROFILES.get(as_param, {})
    name = profile_data.get("name", as_param)

    sidebar_html = _dm_sidebar_for(as_param, lab_id, user_id)
    right_html = (
        '<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;'
        'height:100%;color:#666;gap:14px;padding:40px">'
        '<svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="#c4ccd6" stroke-width="1.2">'
        '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>'
        '<div style="font-size:17px;font-weight:700;color:#222">Your messages</div>'
        '<div style="font-size:13px;color:#888;text-align:center;max-width:240px;line-height:1.5">'
        'Select a conversation from the left to start messaging</div>'
        '</div>'
    )

    nav_av = _npc_av(name, 32, 12) if PROFILES.get(as_param) else f'<div style="width:32px;height:32px;border-radius:50%;background:{avatar_gradient(name)};display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:#fff">{"".join(w[0].upper() for w in name.split()[:2])}</div>'

    return f"""<!DOCTYPE html><html><head><title>Messages — LinkHub</title>{STYLE}{_DM_LAYOUT_CSS}</head><body>
<div class="navbar">
    <a href="/" class="logo" style="text-decoration:none">Link<span style="color:#000">Hub</span></a>
    <div style="flex:1;max-width:280px;margin:0 16px">
        <input placeholder="Search messages…" style="width:100%;padding:7px 14px;border:1px solid #ddd;border-radius:20px;font-size:13px;background:#f3f2ef;outline:none" oninput="filterDms(this.value)">
    </div>
    <div style="display:flex;align-items:center;gap:8px;margin-left:auto">
        {nav_av}
        <span style="font-size:13px;font-weight:600">{_he(name)}</span>
        <span style="font-size:11px;color:#0a66c2;background:#eef3f8;padding:3px 10px;border-radius:12px">Logged in</span>
    </div>
</div>
<div class="msg-layout">
  <div class="msg-left">
    <div style="padding:14px 16px;border-bottom:1px solid #eee;display:flex;align-items:center;justify-content:space-between">
      <div style="font-size:15px;font-weight:700">Messages</div>
    </div>
    <div style="padding:8px 12px;border-bottom:1px solid #eee">
      <input placeholder="Search…" style="width:100%;padding:6px 12px;border:1px solid #e0e0e0;border-radius:20px;font-size:12px;background:#f3f2ef;outline:none" oninput="filterDms(this.value)">
    </div>
    <div style="overflow-y:auto;flex:1">{sidebar_html}</div>
  </div>
  <div class="msg-right">{right_html}</div>
</div>
{_DM_FILTER_JS}
</body></html>"""


@app.get("/compose/{target_slug}", response_class=HTMLResponse)
async def linkhub_compose(target_slug: str, request: Request):
    as_param = request.query_params.get("as", "")
    lab_id = request.query_params.get("lab_id", "")
    user_id = request.query_params.get("user_id", "")

    from_profile = PROFILES.get(as_param, {})
    to_profile = PROFILES.get(target_slug, {})
    from_name = from_profile.get("name", as_param)
    to_name = to_profile.get("name", target_slug)
    to_persona_id = to_profile.get("persona_id", target_slug)
    to_role = to_profile.get("role", "")

    sidebar_html = _dm_sidebar_for(as_param, lab_id, user_id, active_id=target_slug)
    nav_av = _npc_av(from_name, 32, 12)
    to_av = _npc_av(to_name, 44, 16)

    from_persona_id = from_profile.get("persona_id", "")
    send_js = (
        f'var TO_PERSONA_ID="{to_persona_id}",LAB_ID="{lab_id}",USER_ID="{user_id}",FROM_NAME="{from_name}",LOGGED_IN_PERSONA_ID="{from_persona_id}";'
        'function _addBubble(t,sent){'
        'var w=document.getElementById("thread-msgs"),d=document.createElement("div");'
        'var br=sent?"18px 18px 4px 18px":"18px 18px 18px 4px";'
        'var bg=sent?"#0a66c2":"#f0f0f0";var fg=sent?"#fff":"#000";'
        'd.style.cssText="display:flex;align-items:flex-end;gap:8px;margin-bottom:14px;justify-content:"+(sent?"flex-end":"flex-start");'
        'd.innerHTML="<div style=\'max-width:72%;padding:10px 14px;border-radius:"+br+";background:"+bg+";color:"+fg+";font-size:13px;line-height:1.5\'>"'
        '+t.replace(/</g,"&lt;").replace(/>/g,"&gt;")+"</div>";'
        'w.appendChild(d);w.scrollTop=w.scrollHeight;}'
        'function _typing(show){'
        'var e=document.getElementById("typing-ind");if(!show&&e){e.remove();return;}'
        'if(show&&!e){'
        'var w=document.getElementById("thread-msgs"),d=document.createElement("div");'
        'd.id="typing-ind";d.style.cssText="display:flex;align-items:flex-end;gap:8px;margin-bottom:14px";'
        'd.innerHTML="<div style=\'background:#f0f0f0;padding:8px 14px;border-radius:18px;font-size:13px;color:#999\'>typing…</div>";'
        'w.appendChild(d);w.scrollTop=w.scrollHeight;}}'
        'function sendMsg(){'
        'var inp=document.getElementById("msg-input"),txt=inp.value.trim();'
        'if(!txt)return;inp.value="";_addBubble(txt,true);_typing(true);'
        'fetch("http://127.0.0.1:9003/api/dm/send",{method:"POST",headers:{"Content-Type":"application/json"},'
        'body:JSON.stringify({user_id:USER_ID,lab_id:LAB_ID,persona_id:TO_PERSONA_ID,message:txt,logged_in_persona_id:LOGGED_IN_PERSONA_ID})})'
        '.then(r=>r.json()).then(d=>{'
        '_typing(false);'
        'if(d.error){_addBubble("[Error: "+d.error+"]",false);return;}'
        '_addBubble(d.reply||"[no response]",false);'
        'if(d.mission_failed&&!document.getElementById("bust-banner")){'
        'var b=document.createElement("div");b.id="bust-banner";'
        'b.style.cssText="position:fixed;top:60px;left:50%;transform:translateX(-50%);background:#cc0000;color:#fff;padding:10px 24px;border-radius:8px;font-size:13px;font-weight:700;z-index:9999;box-shadow:0 4px 12px rgba(0,0,0,.3)";'
        'b.textContent="⚠ MISSION FAILED — NPC flagged you. Reset the lab to continue.";'
        'document.body.appendChild(b);setTimeout(()=>{if(b.parentNode)b.parentNode.removeChild(b);},8000);}'
        'if(d.flag_found){'
        'var f=document.createElement("div");'
        'f.style.cssText="position:fixed;top:60px;left:50%;transform:translateX(-50%);background:#00880a;color:#fff;padding:10px 24px;border-radius:8px;font-size:13px;font-weight:700;z-index:9999;box-shadow:0 4px 12px rgba(0,0,0,.3)";'
        'f.textContent="🚩 FLAG: "+d.flag_found;'
        'document.body.appendChild(f);}}'
        ')'
        '.catch(()=>{_typing(false);_addBubble("[Connection error]",false);});}'
    )

    return f"""<!DOCTYPE html><html><head><title>Message {_he(to_name)} — LinkHub</title>{STYLE}{_DM_LAYOUT_CSS}</head><body>
<div class="navbar">
    <a href="/" class="logo" style="text-decoration:none">Link<span style="color:#000">Hub</span></a>
    <div style="flex:1;max-width:280px;margin:0 16px">
        <input placeholder="Search messages…" style="width:100%;padding:7px 14px;border:1px solid #ddd;border-radius:20px;font-size:13px;background:#f3f2ef;outline:none" oninput="filterDms(this.value)">
    </div>
    <div style="display:flex;align-items:center;gap:8px;margin-left:auto">
        {nav_av}
        <span style="font-size:13px;font-weight:600">{_he(from_name)}</span>
        <span style="font-size:11px;color:#0a66c2;background:#eef3f8;padding:3px 10px;border-radius:12px">Logged in</span>
    </div>
</div>
<div class="msg-layout">
  <div class="msg-left">
    <div style="padding:14px 16px;border-bottom:1px solid #eee">
      <div style="font-size:15px;font-weight:700">Messages</div>
    </div>
    <div style="padding:8px 12px;border-bottom:1px solid #eee">
      <input placeholder="Search…" style="width:100%;padding:6px 12px;border:1px solid #e0e0e0;border-radius:20px;font-size:12px;background:#f3f2ef;outline:none" oninput="filterDms(this.value)">
    </div>
    <div style="overflow-y:auto;flex:1">{sidebar_html}</div>
  </div>
  <div class="msg-right">
    <div style="padding:12px 18px;border-bottom:1px solid #eee;display:flex;align-items:center;gap:12px;flex-shrink:0">
      {to_av}
      <div style="flex:1;min-width:0">
        <div style="font-size:15px;font-weight:700">{_he(to_name)}</div>
        <div style="font-size:12px;color:#666">{_he(to_role)}</div>
      </div>
      <div style="font-size:11px;background:#fff3e0;color:#b45309;border:1px solid #fcd34d;border-radius:12px;padding:3px 10px;font-weight:600;flex-shrink:0">
        &#x1F464; Sending as {_he(from_name)}
      </div>
    </div>
    <div id="thread-msgs" style="flex:1;overflow-y:auto;padding:18px 22px"></div>
    <div style="padding:12px 16px;border-top:1px solid #eee;display:flex;gap:8px;flex-shrink:0;background:#fff">
      <input id="msg-input" placeholder="Message {_he(to_name)}…"
             style="flex:1;padding:10px 14px;border:1px solid #ddd;border-radius:24px;font-size:13px;outline:none"
             onkeydown="if(event.key==='Enter')sendMsg()">
      <button onclick="sendMsg()" style="background:#0a66c2;color:#fff;border:none;border-radius:50%;width:40px;height:40px;cursor:pointer;font-size:18px;flex-shrink:0">&#x27A4;</button>
    </div>
  </div>
</div>
<script>{send_js}</script>
{_DM_FILTER_JS}
</body></html>"""


_WAVEFORM_SVG = (
    '<svg width="160" height="28" viewBox="0 0 160 28" fill="none" xmlns="http://www.w3.org/2000/svg">'
    + "".join(
        f'<rect x="{4+i*6}" y="{14 - h}" width="4" height="{h*2}" rx="2" fill="#0a66c2" opacity=".7"/>'
        for i, h in enumerate([3,6,10,7,4,8,12,9,5,7,11,8,4,6,9,11,7,5,8,10,6,4,7,9,5,8])
    )
    + "</svg>"
)


def _he(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


_BEN_DM_SIDEBAR = [
    {"id": "rachel",  "name": "Rachel Park",    "role": "Executive Assistant · Meridian Capital",  "preview": "Board deck v4 is uploaded to SharePoint",               "time": "9:14am", "unread": 0, "slug": "rachel-park"},
    {"id": "fintech", "name": "FinTech Forward", "role": "Conference Events Team",                       "preview": "AV check confirmed for May 14 at 10am",                 "time": "2d",     "unread": 1, "slug": None},
    {"id": "jcole",   "name": "James Cole",      "role": "Finance Director · Meridian Capital",     "preview": "Everything staged and ready to execute on your call",   "time": "3d",     "unread": 0, "slug": "james-cole"},
    {"id": "sarah",   "name": "Sarah Whitfield", "role": "CFO · Meridian Capital",                  "preview": "Q1 P&L finalized, sending over shortly",                "time": "1w",     "unread": 0, "slug": "sarah-whitfield"},
]

_BEN_DM_MESSAGES = {
    "rachel": [
        {"from": "recv", "name": "Rachel Park",   "text": "Ben, board deck v3 is on SharePoint. Slide 14 (infrastructure allocation chart) needs your approval before I send to the LPs.",                                    "time": "Apr 9 · 8:47am"},
        {"from": "sent", "name": "Ben Morgan",    "text": "Numbers look right. Approve it.",                                                                                                                                    "time": "Apr 9 · 9:01am"},
        {"from": "recv", "name": "Rachel Park",   "text": "Done. Your UA 1842 flight to Chicago is confirmed — departs Wednesday 7:20am, returns Thursday evening. Car is booked both ways.",                        "time": "Apr 9 · 9:03am"},
        {"from": "sent", "name": "Ben Morgan",    "text": "What time is the LP dinner?",                                                                                                                                        "time": "Apr 9 · 9:06am"},
        {"from": "recv", "name": "Rachel Park",   "text": "7pm at RPM Steak. Adding to your calendar now.",                                                                                                                     "time": "Apr 9 · 9:07am"},
        {"from": "recv", "name": "Rachel Park",   "text": "Also — Churchill’s vet appointment is Friday at 2pm. Want me to reschedule around your calls?",                                                           "time": "Apr 9 · 9:08am"},
        {"from": "sent", "name": "Ben Morgan",    "text": "No, keep it. Maria can take him.",                                                                                                                                   "time": "Apr 9 · 9:11am"},
        {"from": "recv", "name": "Rachel Park",   "text": "Board deck v4 is uploaded to SharePoint.",                                                                                                                           "time": "Apr 9 · 9:14am"},
    ],
    "fintech": [
        {"from": "recv", "name": "FinTech Forward", "text": "Hi Ben — reaching out re: your keynote at FinTech Forward on May 15. We’re finalizing the program guide. Could you provide a 150-word bio and headshot by April 12?", "time": "Mar 28 · 2:14pm"},
        {"from": "sent", "name": "Ben Morgan",      "text": "Use my LinkHub bio. Rachel Park (rachel.park@meridiancap.com) can send a headshot.",                                                                                              "time": "Mar 28 · 4:55pm"},
        {"from": "recv", "name": "FinTech Forward", "text": "Thank you! The AV team will need your slides 48 hours before the keynote in 16:9 format. Any special AV requirements?",                                                          "time": "Apr 1 · 10:21am"},
        {"from": "sent", "name": "Ben Morgan",      "text": "Clicker and confidence monitor. Rachel is handling all slide logistics.",                                                                                                         "time": "Apr 1 · 11:40am"},
        {"from": "recv", "name": "FinTech Forward", "text": "Perfect. One last thing — the pre-keynote mixer is at 6pm on May 14. We’d love for you to join if you’re in town by then.",                                       "time": "Apr 4 · 3:08pm"},
        {"from": "sent", "name": "Ben Morgan",      "text": "Should be able to make it. Have Rachel confirm.",                                                                                                                                 "time": "Apr 4 · 5:22pm"},
        {"from": "recv", "name": "FinTech Forward", "text": "Keynote AV check confirmed for May 14 at 10am. Room opens at 9:30 for setup.",                                                                                                    "time": "Apr 7 · 11:15am"},
    ],
    "jcole": [
        {"from": "recv", "name": "James Cole",  "text": "Ben — Q1 wire reconciliation cleared cleanly across all 14 fund entities. Ready to move to Lighthouse closing when you give the word.",                            "time": "Apr 3 · 3:11pm"},
        {"from": "sent", "name": "Ben Morgan",  "text": "Need one more week on the LP side. Keep the escrow staging ready.",                                                                                                      "time": "Apr 3 · 4:02pm"},
        {"from": "recv", "name": "James Cole",  "text": "Understood. On the Lighthouse wire — do we need to adjust the dual-sign threshold for this size?",                                                                 "time": "Apr 3 · 4:18pm"},
        {"from": "sent", "name": "Ben Morgan",  "text": "Let’s talk. Calling you this afternoon.",                                                                                                                          "time": "Apr 3 · 4:21pm"},
        {"from": "recv", "name": "James Cole",  "text": "Spoke with Sarah. She’s aligned with the adjusted threshold. Controls framework is documented.",                                                                    "time": "Apr 4 · 9:55am"},
        {"from": "voice", "name": "Ben Morgan", "duration": "0:23",                                                                                                                                                               "time": "Apr 7 · 11:42am"},
        {"from": "recv", "name": "James Cole",  "text": "Got it, thanks. I’ll have everything staged and ready to execute on your call.",                                                                                    "time": "Apr 7 · 11:58am"},
    ],
    "sarah": [
        {"from": "recv", "name": "Sarah Whitfield", "text": "Ben — Q1 audit passed. Zero findings, third consecutive year. Operations team did excellent work.",                                                             "time": "Apr 2 · 9:30am"},
        {"from": "sent", "name": "Ben Morgan",       "text": "Excellent. We’ll celebrate at the offsite.",                                                                                                                  "time": "Apr 2 · 10:44am"},
        {"from": "recv", "name": "Sarah Whitfield",  "text": "On another note — I attended the CFO security briefing last week. The deepfake voice demo was genuinely unsettling. We should run a tabletop on this with the finance team.", "time": "Apr 2 · 10:52am"},
        {"from": "sent", "name": "Ben Morgan",       "text": "Schedule it. Add Alex Reed.",                                                                                                                                      "time": "Apr 2 · 11:15am"},
        {"from": "recv", "name": "Sarah Whitfield",  "text": "Done. Also — wire controls update is ready for your signature. The dual-approval threshold changes from March.",                                               "time": "Apr 3 · 8:21am"},
        {"from": "sent", "name": "Ben Morgan",       "text": "Send to Rachel to coordinate a signature time.",                                                                                                                   "time": "Apr 3 · 9:07am"},
        {"from": "recv", "name": "Sarah Whitfield",  "text": "Q1 P&L is finalized, sending over shortly.",                                                                                                                      "time": "Apr 5 · 4:14pm"},
    ],
}

_DM_LAYOUT_CSS = """<style>
.dm-item:hover { background:#f3f2ef !important; }
.msg-layout { display:flex; height:calc(100vh - 52px); overflow:hidden }
.msg-left { width:340px; min-width:240px; border-right:1px solid #e0e0e0; display:flex; flex-direction:column; background:#fff; overflow:hidden }
.msg-right { flex:1; display:flex; flex-direction:column; background:#fff; overflow:hidden; min-width:0 }
</style>"""

_DM_FILTER_JS = """<script>
function filterDms(q) {
  q = q.toLowerCase();
  document.querySelectorAll('.dm-item').forEach(function(el) {
    el.style.display = el.textContent.toLowerCase().includes(q) ? 'flex' : 'none';
  });
}
</script>"""


def _npc_av(name, size=44, font_size=16):
    grad = avatar_gradient(name)
    ini = "".join(w[0].upper() for w in name.split()[:2])
    fs = font_size
    return (
        f'<div style="position:relative;width:{size}px;height:{size}px;min-width:{size}px;flex-shrink:0">'
        f'<img src="/photos/{name}.png" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'flex\'" '
        f'style="width:{size}px;height:{size}px;border-radius:50%;object-fit:cover;">'
        f'<div style="display:none;position:absolute;top:0;left:0;width:{size}px;height:{size}px;border-radius:50%;'
        f'background:{grad};align-items:center;justify-content:center;font-size:{fs}px;font-weight:700;color:#fff">{ini}</div>'
        f'</div>'
    )


def _org_av(name, size=44, font_size=15):
    ini = "".join(w[0].upper() for w in name.split()[:2])
    return (
        f'<div style="width:{size}px;height:{size}px;min-width:{size}px;flex-shrink:0;border-radius:50%;'
        f'background:linear-gradient(135deg,#1e3a5f,#0a66c2);display:flex;align-items:center;'
        f'justify-content:center;font-size:{font_size}px;font-weight:700;color:#fff">{ini}</div>'
    )


def _dm_sidebar_for(as_param, lab_id, user_id, active_id=""):
    """Unified left panel for any persona. ben-morgan gets DM threads; others get colleague list."""
    if as_param == "ben-morgan":
        return _ben_inbox_sidebar(as_param, lab_id, user_id, active_thread=active_id)
    colleagues = [(slug, p) for slug, p in PROFILES.items()
                  if p.get("lab_id") == lab_id and slug != as_param and p.get("is_persona")]
    if not colleagues:
        return '<div style="padding:20px;font-size:13px;color:#999;text-align:center">No contacts found</div>'
    html = ""
    for slug, p in colleagues:
        is_active = active_id == slug
        bg = "background:#eef3f8;border-left:3px solid #0a66c2;" if is_active else "background:transparent;border-left:3px solid transparent;"
        av = _npc_av(p["name"], 44, 15)
        html += (
            f'<a href="/compose/{slug}?as={as_param}&lab_id={lab_id}&user_id={user_id}" class="dm-item"'
            f' style="{bg}display:flex;align-items:center;gap:10px;padding:11px 14px;text-decoration:none;color:#000;border-bottom:1px solid #f0f0f0;">'
            f'{av}'
            f'<div style="flex:1;min-width:0;overflow:hidden">'
            f'<div style="font-size:13px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{_he(p["name"])}</div>'
            f'<div style="font-size:11px;color:#666;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:2px">{_he(p["role"])}</div>'
            f'</div>'
            f'</a>'
        )
    return html


def _ben_inbox_sidebar(as_param, lab_id, user_id, active_thread=""):
    html = ""
    for t in _BEN_DM_SIDEBAR:
        tid = t["id"]
        tname = t["name"]
        slug = t.get("slug")
        av = _npc_av(tname, 44, 15) if slug else _org_av(tname, 44, 14)
        is_active = active_thread == tid
        bg = "background:#eef3f8;border-left:3px solid #0a66c2;" if is_active else "background:transparent;border-left:3px solid transparent;"
        fw = "700" if t.get("unread") else "600"
        pc = "#111" if t.get("unread") else "#666"
        ubadge = (
            f'<span style="background:#cc1016;color:#fff;border-radius:9px;padding:0 6px;font-size:10px;font-weight:700;line-height:17px">{t["unread"]}</span>'
            if t.get("unread") else ""
        )
        html += (
            f'<a href="/messages/{tid}?as={as_param}&lab_id={lab_id}&user_id={user_id}" class="dm-item"'
            f' style="{bg}display:flex;align-items:center;gap:10px;padding:11px 14px;text-decoration:none;color:#000;border-bottom:1px solid #f0f0f0;">'
            f'{av}'
            f'<div style="flex:1;min-width:0;overflow:hidden">'
            f'<div style="font-size:13px;font-weight:{fw};white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{_he(tname)}</div>'
            f'<div style="font-size:11px;color:{pc};white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:2px">{_he(t["preview"])}</div>'
            f'</div>'
            f'<div style="display:flex;flex-direction:column;align-items:flex-end;gap:3px;flex-shrink:0">'
            f'<span style="font-size:10px;color:#999;white-space:nowrap">{t["time"]}</span>'
            f'{ubadge}'
            f'</div>'
            f'</a>'
        )
    return html


@app.get("/messages/{thread}", response_class=HTMLResponse)
async def linkhub_dm_thread(thread: str, request: Request):
    as_param = request.query_params.get("as", "")
    lab_id = request.query_params.get("lab_id", "")
    user_id = request.query_params.get("user_id", "")

    if as_param != "ben-morgan" or thread not in _BEN_DM_MESSAGES:
        return HTMLResponse("<h2 style='font-family:sans-serif;padding:40px;color:#666'>Thread not found.</h2>", status_code=404)

    profile_data = PROFILES.get(as_param, {})
    me_name = profile_data.get("name", "Ben Morgan")
    thread_meta = next((t for t in _BEN_DM_SIDEBAR if t["id"] == thread), {})
    other_name = thread_meta.get("name", thread)
    other_role = thread_meta.get("role", "")
    other_slug = thread_meta.get("slug")
    download_url = f"/api/voice-note/download?as={as_param}&lab_id={lab_id}&user_id={user_id}"

    # Build messages HTML
    msgs_html = ""
    for msg in _BEN_DM_MESSAGES[thread]:
        direction = msg["from"]
        mtime = msg.get("time", "")

        if direction == "voice":
            av = _npc_av(me_name, 30, 10)
            msgs_html += (
                f'<div style="display:flex;align-items:flex-end;gap:8px;margin-bottom:16px;justify-content:flex-end">'
                f'<div>'
                f'<div style="background:#e8f4fd;border:1px solid #b3d4f0;border-radius:12px;padding:10px 14px;'
                f'display:flex;align-items:center;gap:10px">'
                f'<div style="width:32px;height:32px;border-radius:50%;background:#0a66c2;display:flex;align-items:center;'
                f'justify-content:center;flex-shrink:0">'
                f'<svg width="10" height="12" viewBox="0 0 10 12" fill="#fff"><polygon points="0,0 10,6 0,12"/></svg>'
                f'</div>'
                f'{_WAVEFORM_SVG}'
                f'<span style="font-size:11px;color:#666;min-width:28px">{msg["duration"]}</span>'
                f'</div>'
                f'<div style="margin-top:6px;display:flex;align-items:center;justify-content:flex-end;gap:10px">'
                f'<span style="font-size:10px;color:#999">{mtime}</span>'
                f'<a href="{download_url}" download="ben_morgan_voice_9a3f.sfvoice" '
                f'style="background:#0a66c2;color:#fff;border-radius:20px;padding:5px 12px;font-size:11px;'
                f'font-weight:600;text-decoration:none">&#x2193; Save voice note</a>'
                f'</div>'
                f'</div>'
                f'{av}'
                f'</div>'
            )
        elif direction == "sent":
            av = _npc_av(me_name, 30, 10)
            msgs_html += (
                f'<div style="display:flex;align-items:flex-end;gap:8px;margin-bottom:14px;justify-content:flex-end">'
                f'<div style="max-width:68%">'
                f'<div style="background:#0a66c2;color:#fff;border-radius:18px 18px 4px 18px;padding:10px 14px;'
                f'font-size:13px;line-height:1.5">{_he(msg["text"])}</div>'
                f'<div style="font-size:10px;color:#999;margin-top:3px;text-align:right">{mtime}</div>'
                f'</div>'
                f'{av}'
                f'</div>'
            )
        else:
            av = _npc_av(other_name, 30, 10) if other_slug else _org_av(other_name, 30, 10)
            msgs_html += (
                f'<div style="display:flex;align-items:flex-end;gap:8px;margin-bottom:14px">'
                f'{av}'
                f'<div style="max-width:68%">'
                f'<div style="background:#f0f0f0;color:#000;border-radius:18px 18px 18px 4px;padding:10px 14px;'
                f'font-size:13px;line-height:1.5">{_he(msg["text"])}</div>'
                f'<div style="font-size:10px;color:#999;margin-top:3px">{mtime}</div>'
                f'</div>'
                f'</div>'
            )

    sidebar_html = _ben_inbox_sidebar(as_param, lab_id, user_id, active_thread=thread)
    nav_av = _npc_av(me_name, 32, 12)
    oth_av_hdr = _npc_av(other_name, 44, 16) if other_slug else _org_av(other_name, 44, 15)
    sandbox_note = (
        '<div style="padding:8px 16px;background:#fff8e1;border-top:1px solid #f0c040;font-size:11px;color:#856404;flex-shrink:0">'
        '<strong>&#x26A0; Sandbox:</strong> This is a simulated voice note. Real extraction from private accounts constitutes unauthorized access.</div>'
    ) if thread == "jcole" else ""

    # Send box: only for threads with a real NPC persona to respond
    other_persona_id = PROFILES.get(other_slug, {}).get("persona_id", "") if other_slug else ""
    if other_persona_id:
        _me_persona_id = PROFILES.get(as_param, {}).get('persona_id', '')
        send_js = (
            f'var _PID="{other_persona_id}",_LID="{lab_id}",_UID="{user_id}",_MN="{_he(me_name)}",_LPID="{_me_persona_id}";'
            'function _bubble(t,sent){'
            'var w=document.getElementById("thread-msgs"),d=document.createElement("div");'
            'var br=sent?"18px 18px 4px 18px":"18px 18px 18px 4px";'
            'var bg=sent?"#0a66c2":"#f0f0f0";var fg=sent?"#fff":"#000";'
            'd.style.cssText="display:flex;align-items:flex-end;gap:8px;margin-bottom:14px;justify-content:"+(sent?"flex-end":"flex-start");'
            'd.innerHTML="<div style=\'max-width:68%;padding:10px 14px;border-radius:"+br+";background:"+bg+";color:"+fg+";font-size:13px;line-height:1.5\'>"'
            '+t.replace(/</g,"&lt;").replace(/>/g,"&gt;")+"</div>";'
            'w.appendChild(d);w.scrollTop=w.scrollHeight;}'
            'function _tind(show){'
            'var e=document.getElementById("tind");if(!show&&e){e.remove();return;}'
            'if(show&&!e){'
            'var w=document.getElementById("thread-msgs"),d=document.createElement("div");'
            'd.id="tind";d.style.cssText="display:flex;margin-bottom:14px";'
            'd.innerHTML="<div style=\'background:#f0f0f0;padding:8px 14px;border-radius:18px;font-size:13px;color:#999\'>typing…</div>";'
            'w.appendChild(d);w.scrollTop=w.scrollHeight;}}'
            'function sendMsg(){'
            'var inp=document.getElementById("reply-input"),txt=inp.value.trim();'
            'if(!txt)return;inp.value="";_bubble(txt,true);_tind(true);'
            'fetch("http://127.0.0.1:9003/api/dm/send",{method:"POST",headers:{"Content-Type":"application/json"},'
            'body:JSON.stringify({user_id:_UID,lab_id:_LID,persona_id:_PID,message:txt,logged_in_persona_id:_LPID})})'
            '.then(r=>r.json()).then(d=>{_tind(false);_bubble(d.reply||"[no response]",false);})'
            '.catch(()=>{_tind(false);_bubble("[Connection error]",false);});}'
            'document.getElementById("thread-msgs").scrollTop=9999;'
        )
        reply_box = (
            f'<div style="padding:12px 16px;border-top:1px solid #eee;display:flex;gap:8px;flex-shrink:0;background:#fff">'
            f'<input id="reply-input" placeholder="Reply as {_he(me_name)}…" '
            f'style="flex:1;padding:10px 14px;border:1px solid #ddd;border-radius:24px;font-size:13px;outline:none" '
            f'onkeydown="if(event.key===\'Enter\')sendMsg()">'
            f'<button onclick="sendMsg()" style="background:#0a66c2;color:#fff;border:none;border-radius:50%;width:40px;height:40px;cursor:pointer;font-size:18px;flex-shrink:0">&#x27A4;</button>'
            f'</div>'
        )
    else:
        send_js = 'document.getElementById("thread-msgs").scrollTop=9999;'
        reply_box = ""

    return f"""<!DOCTYPE html><html><head><title>{_he(other_name)} — Messages · LinkHub</title>{STYLE}{_DM_LAYOUT_CSS}</head><body>
<div class="navbar">
    <a href="/" class="logo" style="text-decoration:none">Link<span style="color:#000">Hub</span></a>
    <div style="flex:1;max-width:280px;margin:0 16px">
        <input placeholder="Search messages…" style="width:100%;padding:7px 14px;border:1px solid #ddd;border-radius:20px;font-size:13px;background:#f3f2ef;outline:none" oninput="filterDms(this.value)">
    </div>
    <div style="display:flex;align-items:center;gap:8px;margin-left:auto">
        {nav_av}
        <span style="font-size:13px;font-weight:600">{_he(me_name)}</span>
        <span style="font-size:11px;color:#0a66c2;background:#eef3f8;padding:3px 10px;border-radius:12px">Logged in</span>
    </div>
</div>
<div class="msg-layout">
  <div class="msg-left">
    <div style="padding:14px 16px;border-bottom:1px solid #eee;display:flex;align-items:center">
      <div style="font-size:15px;font-weight:700;flex:1">Messages</div>
    </div>
    <div style="padding:8px 12px;border-bottom:1px solid #eee">
      <input placeholder="Search…" style="width:100%;padding:6px 12px;border:1px solid #e0e0e0;border-radius:20px;font-size:12px;background:#f3f2ef;outline:none" oninput="filterDms(this.value)">
    </div>
    <div style="overflow-y:auto;flex:1">{sidebar_html}</div>
  </div>
  <div class="msg-right">
    <div style="padding:12px 18px;border-bottom:1px solid #eee;display:flex;align-items:center;gap:12px;flex-shrink:0">
      {oth_av_hdr}
      <div>
        <div style="font-size:15px;font-weight:700">{_he(other_name)}</div>
        <div style="font-size:12px;color:#666">{_he(other_role)}</div>
      </div>
    </div>
    <div id="thread-msgs" style="flex:1;overflow-y:auto;padding:18px 22px">{msgs_html}</div>
    {sandbox_note}
    {reply_box}
  </div>
</div>
<script>{send_js}</script>
{_DM_FILTER_JS}
</body></html>"""


@app.get("/api/voice-note/download")
async def voice_note_download():
    import json as _json
    _sfvoice = {
        "type": "sf_voice_sample",
        "persona": "ben_morgan",
        "quality": 0.97,
        "source": "linkhub_dm",
        "duration": "0:23",
        "thread": "jcole",
        "captured_at": "2024-04-07T11:42:00Z",
    }
    from fastapi.responses import Response
    return Response(
        content=_json.dumps(_sfvoice, indent=2).encode(),
        media_type="application/octet-stream",
        headers={"Content-Disposition": 'attachment; filename="ben_morgan_voice_9a3f.sfvoice"'},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9003)
