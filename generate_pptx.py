"""
HandLingo Presentation Generator
Run this script to generate 'HandLingo_Presentation.pptx'.
Prerequisite: pip install python-pptx
"""

import sys

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    from pptx.enum.shapes import MSO_SHAPE
except ImportError:
    print("\n[!] 'python-pptx' is not installed.")
    print("Please install it by running: pip install python-pptx\n")
    sys.exit(1)


def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Brand Colors
    COLOR_BG = RGBColor(11, 15, 25)         # #0B0F19 Dark Navy
    COLOR_CARD = RGBColor(23, 32, 51)       # #172033 Card Surface
    COLOR_CYAN = RGBColor(6, 182, 212)      # #06B6D4 Accent Cyan
    COLOR_PURPLE = RGBColor(139, 92, 246)   # #8B5CF6 Accent Purple
    COLOR_TEXT = RGBColor(248, 250, 252)    # #F8FAFC White Text
    COLOR_MUTED = RGBColor(148, 163, 184)   # #94A3B8 Muted Text

    blank_layout = prs.slide_layouts[6]

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_BG
        bg.line.fill.background()
        return bg

    def add_header(slide, tag_text, title_text):
        # Header Tag
        tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.5), Inches(0.4))
        tf_tag = tag_box.text_frame
        tf_tag.word_wrap = True
        p_tag = tf_tag.paragraphs[0]
        p_tag.text = tag_text.upper()
        p_tag.font.size = Pt(11)
        p_tag.font.bold = True
        p_tag.font.color.rgb = COLOR_CYAN

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(11.5), Inches(0.8))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(26)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_TEXT

    def add_card(slide, left, top, width, height, title, items):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD
        card.line.color.rgb = RGBColor(51, 65, 85)
        card.line.width = Pt(1)

        txBox = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.2), width - Inches(0.4), height - Inches(0.4))
        tf = txBox.text_frame
        tf.word_wrap = True

        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(16)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_CYAN
        p_t.space_after = Pt(8)

        for itm in items:
            p = tf.add_paragraph()
            p.text = f"• {itm}"
            p.font.size = Pt(13)
            p.font.color.rgb = COLOR_MUTED
            p.space_after = Pt(6)

    # -------------------------------------------------------------
    # SLIDE 1: Title Slide
    # -------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    tbox = s1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(4.0))
    tf1 = tbox.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    p0.text = "AI & COMPUTER VISION PROJECT"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_CYAN
    p0.space_after = Pt(12)

    p1 = tf1.add_paragraph()
    p1.text = "HANDLINGO"
    p1.font.size = Pt(44)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_TEXT
    p1.space_after = Pt(16)

    p2 = tf1.add_paragraph()
    p2.text = "AI-Powered Hand Gesture Communication & Touchless Interaction Platform"
    p2.font.size = Pt(20)
    p2.font.color.rgb = COLOR_PURPLE
    p2.space_after = Pt(24)

    p3 = tf1.add_paragraph()
    p3.text = "Translating Sign Language to Speech | Redefining Touchless Human-Computer Interaction"
    p3.font.size = Pt(14)
    p3.font.color.rgb = COLOR_MUTED

    # -------------------------------------------------------------
    # SLIDE 2: Problem Statement
    # -------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "Problem Statement", "The Communication & Touch Interaction Barrier")
    add_card(s2, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), "Sign Language Inaccessibility", [
        "Over 70 million deaf individuals globally rely on sign language as primary communication.",
        "General public lacks sign language comprehension, causing isolation in daily life.",
        "Heavy reliance on human translators who are scarce, costly, and unavailable 24/7.",
        "Critical communication gaps in hospitals, educational institutions, and public offices."
    ])
    add_card(s2, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "Physical Contact Limitations", [
        "Traditional computing depends on keyboards, mice, and touch displays.",
        "Hygienic constraints: Sterile environments (surgery, labs) cannot touch peripherals.",
        "Convenience hurdles: Tedious slide navigation during presentations or lectures.",
        "Wearable tracking hardware (data gloves) is expensive, bulky, and fragile."
    ])

    # -------------------------------------------------------------
    # SLIDE 3: Objectives of the Project
    # -------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "Objectives", "Core Goals of HandLingo")
    add_card(s3, Inches(0.8), Inches(1.8), Inches(3.7), Inches(2.4), "1. Sign Translation", [
        "Track 21 hand landmarks in real-time.",
        "Translate letters (A-Z) into coherent text."
    ])
    add_card(s3, Inches(4.8), Inches(1.8), Inches(3.7), Inches(2.4), "2. Speech Output (TTS)", [
        "Synthesize translated text to vocal audio.",
        "Enable seamless dialogue with non-signers."
    ])
    add_card(s3, Inches(8.8), Inches(1.8), Inches(3.7), Inches(2.4), "3. Touchless Audio Control", [
        "Pinch distance scales system volume dynamically.",
        "Live on-screen visual feedback bar."
    ])
    add_card(s3, Inches(0.8), Inches(4.5), Inches(3.7), Inches(2.4), "4. Virtual Air Drawing", [
        "Index finger acts as digital stylus.",
        "Draw, select colors, and erase in air."
    ])
    add_card(s3, Inches(4.8), Inches(4.5), Inches(3.7), Inches(2.4), "5. Slide & Media Control", [
        "Hand swipes advance or revert presentation slides.",
        "Hands-free media playback navigation."
    ])
    add_card(s3, Inches(8.8), Inches(4.5), Inches(3.7), Inches(2.4), "6. Ubiquitous & Affordable", [
        "Zero sensory gloves required.",
        "Works smoothly on any standard web camera."
    ])

    # -------------------------------------------------------------
    # SLIDE 4: Proposed Solution
    # -------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "Proposed Solution", "Unified Computer Vision Gesture Hub")
    add_card(s4, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), "All-In-One Dual Capability", [
        "Combines Assistive Communication and Touchless HCI into a single platform.",
        "Pure Software Solution: Powered by single RGB camera, eliminating data gloves.",
        "Sub-30ms Latency: Fast mathematical spatial modeling guarantees zero noticeable delay.",
        "Web-First Dashboard: Easy-to-use Flask browser portal with one-click toggles."
    ])
    add_card(s4, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "Why HandLingo Stands Out", [
        "Instant Hand Acquisition: Calibrates immediately when hands enter camera view.",
        "Robust Process Isolation: Prevents webcam freeze via decoupled process threads.",
        "Scalable Architecture: Easily extends to new signs and custom desktop gestures.",
        "High Accessibility: Operates on budget laptops and consumer-grade hardware."
    ])

    # -------------------------------------------------------------
    # SLIDE 5: System Architecture
    # -------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "Architecture", "HandLingo End-to-End Pipeline")
    add_card(s5, Inches(0.8), Inches(1.8), Inches(2.7), Inches(4.8), "1. Video Capture", [
        "Webcam video stream captured via OpenCV.",
        "Frames converted from BGR to RGB color space.",
        "Optimized 30 FPS processing."
    ])
    add_card(s5, Inches(3.7), Inches(1.8), Inches(2.7), Inches(4.8), "2. Landmark Tracking", [
        "MediaPipe Hands pipeline.",
        "Detects palm bounds and maps 21 3D hand joints.",
        "High-accuracy finger coordinates (X, Y, Z)."
    ])
    add_card(s5, Inches(6.6), Inches(1.8), Inches(2.7), Inches(4.8), "3. Logic Engine", [
        "Euclidean distance calculations.",
        "Finger fold & angle analysis.",
        "Sign classification & gesture dispatch."
    ])
    add_card(s5, Inches(9.5), Inches(1.8), Inches(2.9), Inches(4.8), "4. OS & UI Action", [
        "Text-to-Speech audio output.",
        "PyCaw: Master volume control.",
        "PyAutoGUI: Slide & mouse emulation.",
        "OpenCV canvas overlay."
    ])

    # -------------------------------------------------------------
    # SLIDE 6: Technologies Used
    # -------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "Technology Stack", "Robust Libraries & Frameworks")
    add_card(s6, Inches(0.8), Inches(1.8), Inches(2.7), Inches(4.8), "Vision & ML", [
        "MediaPipe: High-fidelity 21-point 3D hand landmark tracking.",
        "OpenCV: Real-time image processing & camera video feed capture.",
        "NumPy: Coordinate math and array processing."
    ])
    add_card(s6, Inches(3.7), Inches(1.8), Inches(2.7), Inches(4.8), "Backend Framework", [
        "Python 3: Core programming language.",
        "Flask: Web server, routing, and REST API endpoints.",
        "Subprocess: Background process lifecycle management."
    ])
    add_card(s6, Inches(6.6), Inches(1.8), Inches(2.7), Inches(4.8), "OS & Audio", [
        "PyCaw / comtypes: Windows Core Audio API volume integration.",
        "PyAutoGUI: Virtual keyboard strokes for presentation control.",
        "TTS Engine: Speech synthesis."
    ])
    add_card(s6, Inches(9.5), Inches(1.8), Inches(2.9), Inches(4.8), "Frontend & Security", [
        "HTML5 / CSS3 / JS: Sleek, responsive web dashboard.",
        "SSL / pyOpenSSL: HTTPS camera permission compliance in browsers."
    ])

    # -------------------------------------------------------------
    # SLIDE 7: Working Methodology
    # -------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "Methodology", "Step-by-Step Gesture Processing")
    add_card(s7, Inches(0.8), Inches(1.8), Inches(3.7), Inches(4.8), "Phase 1: Input & Extraction", [
        "Webcam captures real-time video frames.",
        "MediaPipe locates palm bounding boxes.",
        "Extracts 21 landmarks: Thumb Tip (4), Index Tip (8), Middle Tip (12), Wrist (0)."
    ])
    add_card(s7, Inches(4.8), Inches(1.8), Inches(3.7), Inches(4.8), "Phase 2: Mathematical Analysis", [
        "Computes Euclidean distances between landmark pairs.",
        "Checks finger tip elevation relative to pip/dip knuckles.",
        "Calculates pinch proximity, open hand, and closed fist states."
    ])
    add_card(s7, Inches(8.8), Inches(1.8), Inches(3.7), Inches(4.8), "Phase 3: Trigger Execution", [
        "Volume: Linear interpolation maps distance [20-200px] to volume dB.",
        "Air Draw: Index tip positions recorded into drawing array.",
        "Presentation: Directional sweeps fire simulated Left/Right keystrokes.",
        "Translation: Detected character appended to text buffer."
    ])

    # -------------------------------------------------------------
    # SLIDE 8: Major Features & Modules
    # -------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "Modules & Features", "Core Platform Functionalities")
    add_card(s8, Inches(0.8), Inches(1.8), Inches(5.6), Inches(2.3), "1. Sign Language to Speech", [
        "Translates signs (A, B, C, D...) into text letters.",
        "Concatenates letters into sentences with TTS audio speech."
    ])
    add_card(s8, Inches(6.8), Inches(1.8), Inches(5.6), Inches(2.3), "2. Smart Volume Controller", [
        "Thumb-index pinch distance modulates master system sound.",
        "Dynamic on-screen HUD percentage & level indicator."
    ])
    add_card(s8, Inches(0.8), Inches(4.4), Inches(5.6), Inches(2.3), "3. Virtual Air Drawing Canvas", [
        "Draw in mid-air with index finger.",
        "Palette selection (Red, Green, Blue, Eraser) and clear-canvas swipe."
    ])
    add_card(s8, Inches(6.8), Inches(4.4), Inches(5.6), Inches(2.3), "4. Presentation & Media Controller", [
        "Gesture swipe to move forward or backward in slide presentations.",
        "Hands-free media playback navigation (Play, Pause, Skip)."
    ])

    # -------------------------------------------------------------
    # SLIDE 9: Applications, Advantages & Scope
    # -------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "Value Proposition", "Applications, Advantages & Future Scope")
    add_card(s9, Inches(0.8), Inches(1.8), Inches(3.7), Inches(4.8), "Real-World Applications", [
        "Assistive Communication for deaf & hard-of-hearing community.",
        "Operating rooms & labs requiring antiseptic touch-free navigation.",
        "Classrooms & auditoriums for seamless presenter slide controls.",
        "Public kiosks, ATMs, and elevators to minimize germ transmission."
    ])
    add_card(s9, Inches(4.8), Inches(1.8), Inches(3.7), Inches(4.8), "Key Advantages", [
        "Zero Hardware Costs: Utilizes standard laptop webcams.",
        "High Responsiveness: Ultra-low latency landmark processing.",
        "Universal Accessibility: Clean web-based user interface.",
        "Contactless Hygiene: 100% germ-free digital control."
    ])
    add_card(s9, Inches(8.8), Inches(1.8), Inches(3.7), Inches(4.8), "Future Scope", [
        "Full Continuous Sign Recognition with Deep Learning (LSTMs).",
        "Mobile App support for Android and iOS smartphones.",
        "Multi-language translation (Spanish, French, Hindi, Japanese).",
        "Spatial AR/VR integration with smart glasses."
    ])

    # -------------------------------------------------------------
    # SLIDE 10: Conclusion & Future Enhancements
    # -------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "Summary & Roadmap", "Conclusion & Future Enhancements")
    add_card(s10, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), "Conclusion", [
        "HandLingo successfully bridges human communication and touchless interaction.",
        "Proves that accessible computer vision can replace costly sensory peripherals.",
        "Delivers dual value: an assistive translation tool and a versatile productivity suite.",
        "Establishes a solid groundwork for intuitive, touchless Human-Computer Interaction."
    ])
    add_card(s10, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "Roadmap & Enhancements", [
        "Vocabulary Expansion: Extend beyond finger spelling to 1000+ continuous phrases.",
        "Edge Device Optimization: Deploy lightweight quantized models on Raspberry Pi.",
        "Bidirectional Mode: Speech-to-Sign avatar generation for complete conversations.",
        "Two-Hand Gesture Support for complex spatial CAD & 3D object manipulation."
    ])

    output_filename = "HandLingo_Presentation.pptx"
    prs.save(output_filename)
    print(f"\n[✓] Presentation successfully created: {output_filename}\n")


if __name__ == "__main__":
    create_presentation()
