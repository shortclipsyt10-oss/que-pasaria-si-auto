"""Dibujos planos del estilo de los primeros videos (escenarios, personas, animales y objetos).
Copiados del motor hecho a mano; el estilo de los 6 primeros videos sale de aquí."""
import cairo, math, random
W, H, FPS = 1080, 1920, 30
FONT = "Inter Display Black"
PI = math.pi
def ease(x):
    x = max(0, min(1, x)); return 1 - (1 - x) ** 3
def back(x):
    x = max(0, min(1, x)); c = 2.2; return max(0.001, 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2)
def hexc(h, a=1):
    h = h.lstrip('#'); h = ''.join(ch*2 for ch in h) if len(h) == 3 else h; return (int(h[0:2], 16)/255, int(h[2:4], 16)/255, int(h[4:6], 16)/255, a)
def col(c, hx, a=1): c.set_source_rgba(*hexc(hx, a))
# ---------- primitives ----------
def rrect(c, x, y, w, h, r):
    c.new_sub_path(); c.arc(x+w-r, y+r, r, -PI/2, 0); c.arc(x+w-r, y+h-r, r, 0, PI/2)
    c.arc(x+r, y+h-r, r, PI/2, PI); c.arc(x+r, y+r, r, PI, 3*PI/2); c.close_path()

def ell(c, x, y, rx, ry):
    c.save(); c.translate(x, y); c.scale(rx, ry); c.arc(0, 0, 1, 0, 2*PI); c.restore()

def text(c, s, x, y, size, fill="#ffffff", stroke="#111111", sw=0.16, anchor="c", scale=1, rot=0, alpha=1):
    c.save(); c.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(size); e = c.text_extents(s)
    c.translate(x, y); c.rotate(rot); c.scale(scale, scale)
    ox = -e.x_advance/2 if anchor == "c" else (0 if anchor == "l" else -e.x_advance)
    c.move_to(ox, size*0.36); c.text_path(s)
    if stroke:
        c.set_line_width(size*sw); c.set_line_join(cairo.LINE_JOIN_ROUND); col(c, stroke, alpha); c.stroke_preserve()
    col(c, fill, alpha); c.fill(); c.restore()
    return e.x_advance * scale

def text_w(c, s, size):
    c.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(size)
    return c.text_extents(s).x_advance

def sky(c, top="#7fd3ff", bot="#ffe6a8", ground="#e0833c", gy=1250, ground2="#c96a2b"):
    g = cairo.LinearGradient(0, 0, 0, gy); g.add_color_stop_rgba(0, *hexc(top)); g.add_color_stop_rgba(1, *hexc(bot))
    c.set_source(g); c.rectangle(-400, -400, W+800, gy+400); c.fill()
    col(c, ground); c.rectangle(-400, gy, W+800, H-gy+600); c.fill()
    col(c, ground2);
    for i in range(14):
        rnd = random.Random(i); x = rnd.uniform(-200, W+200); y = gy + rnd.uniform(40, 650)
        ell(c, x, y, rnd.uniform(40, 120), rnd.uniform(8, 18)); c.fill()

def sun(c, x, y, r, t, colr="#ffd23f"):
    c.save(); c.translate(x, y); c.rotate(t*0.3); col(c, colr, 0.35)
    for i in range(12):
        c.save(); c.rotate(i*PI/6); c.move_to(0, 0); c.line_to(r*2.1, -r*0.25); c.line_to(r*2.1, r*0.25); c.close_path(); c.fill(); c.restore()
    c.restore(); col(c, colr); c.arc(x, y, r, 0, 2*PI); c.fill()

def cloud(c, x, y, s):
    col(c, "#ffffff", 0.95)
    for dx, dy, r in [(0, 0, 60), (60, -25, 70), (130, 0, 55), (65, 15, 60)]:
        c.arc(x+dx*s, y+dy*s, r*s, 0, 2*PI); c.fill()

def emu(c, x, y, s=1, t=0, run=0, face=1, peck=0, helmet=False, medal=False, sad=False, blink=True, wave=0):
    """x,y = feet position. run: leg speed (0=still). face: 1 right, -1 left"""
    c.save(); c.translate(x, y); c.scale(s*face, s)
    ph = t*run*12
    bob = abs(math.sin(ph))*10 if run else 0
    c.translate(0, -bob)
    # legs
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    for k, off in [(0, 0), (1, PI)]:
        a = math.sin(ph+off)*0.7 if run else (0.12 if k == 0 else -0.12)
        hipx, hipy = -5 + k*10, -230
        kx = hipx + math.sin(a)*90 + 15; ky = hipy + math.cos(a)*100
        fx = kx + math.sin(a-0.6)*-0 + math.sin(a)*40 - 10; fy = 0 + bob - (max(0, math.sin(ph+off))*35 if run else 0)
        col(c, "#6b4a2b" if k == 0 else "#7d5a37"); c.set_line_width(16)
        c.move_to(hipx, hipy); c.line_to(kx, ky); c.line_to(fx, fy); c.stroke()
        c.set_line_width(9); c.move_to(fx-18, fy); c.line_to(fx+30, fy); c.stroke()
        c.move_to(fx, fy); c.line_to(fx+22, fy-12); c.stroke()
    # body
    col(c, "#4a3b33"); ell(c, -10, -290, 125, 95); c.fill()
    col(c, "#5d4a3f")
    for i in range(7):
        ang = PI*0.55 + i*0.22; c.move_to(-10+math.cos(ang)*100, -290+math.sin(ang)*70)
        c.line_to(-10+math.cos(ang)*150, -270+math.sin(ang)*90); c.set_line_width(18); c.stroke()
    col(c, "#6a5649"); ell(c, 0, -305, 90, 55); c.fill()
    # wing wave
    if wave:
        c.save(); c.translate(40, -310); c.rotate(-0.8 + math.sin(t*10)*0.5*wave)
        col(c, "#3b2f29"); ell(c, 50, 0, 60, 22); c.fill(); c.restore()
    # neck
    hx, hy = 70 + peck*90, -520 + peck*330
    c.set_line_width(42); col(c, "#5b6f8a")
    c.move_to(55, -330); c.curve_to(95, -400, 50 + peck*80, -460 + peck*200, hx, hy); c.stroke()
    # head
    col(c, "#6f84a0"); ell(c, hx+5, hy, 40, 34); c.fill()
    if helmet:
        col(c, "#6b7a3a"); c.arc(hx+5, hy-8, 46, PI, 2*PI); c.fill()
        c.rectangle(hx-55, hy-12, 120, 12); c.fill()
    # beak
    col(c, "#2b2b2b"); c.move_to(hx+30, hy-8); c.line_to(hx+85, hy+4); c.line_to(hx+30, hy+14); c.close_path(); c.fill()
    # eye
    bl = 1.0
    if blink and (t % 3.1) < 0.12: bl = 0.15
    col(c, "#ffffff"); ell(c, hx+12, hy-8, 15, 15*bl); c.fill()
    col(c, "#d14b1f"); ell(c, hx+15, hy-8, 9, 9*bl); c.fill()
    col(c, "#000000"); ell(c, hx+17, hy-8, 5, 5*bl); c.fill()
    if sad:
        c.set_line_width(6); col(c, "#000"); c.move_to(hx-5, hy-30); c.line_to(hx+28, hy-22); c.stroke()
    else:
        c.set_line_width(6); col(c, "#000"); c.move_to(hx-2, hy-24); c.line_to(hx+30, hy-30); c.stroke()
    if medal:
        c.set_line_width(8); col(c, "#d63031"); c.move_to(40, -430); c.line_to(75, -360); c.line_to(105, -420); c.stroke()
        col(c, "#ffd23f"); c.arc(75, -350, 24, 0, 2*PI); c.fill(); col(c, "#e1a500"); c.arc(75, -350, 14, 0, 2*PI); c.fill()
    c.restore()

def person(c, x, y, s=1, t=0, walk=0, hat="slouch", shirt="#8a7a45", face=1, gun=False, flag=False, sad=False, mustache=False, armup=0, armup2=0, skirt=None, skin="#f2c29b", hair=None, beard=False):
    c.save(); c.translate(x, y); c.scale(s*face, s)
    ph = t*walk*10; c.set_line_cap(cairo.LINE_CAP_ROUND)
    bob = abs(math.sin(ph))*6 if walk else 0; c.translate(0, -bob)
    # legs
    for off in (0, PI):
        a = math.sin(ph+off)*0.45 if walk else 0
        col(c, "#4a4030"); c.set_line_width(26)
        c.move_to(0, -170); c.line_to(math.sin(a)*90, -5+bob); c.stroke()
        col(c, "#2b2118"); ell(c, math.sin(a)*90+12, 0+bob, 24, 12); c.fill()
    # body
    col(c, shirt); rrect(c, -48, -330, 96, 175, 30); c.fill()
    if skirt:
        col(c, skirt); c.move_to(-48, -200); c.line_to(48, -200); c.line_to(85, -40); c.line_to(-85, -40); c.close_path(); c.fill()
    col(c, "#5b4a2a"); c.rectangle(-48, -190, 96, 16); c.fill()
    # arms
    c.set_line_width(24); col(c, shirt)
    if flag:
        c.move_to(20, -300); c.line_to(70, -400); c.stroke()
        col(c, "#5a3d1e"); c.set_line_width(8); c.move_to(70, -330); c.line_to(70, -560); c.stroke()
        wv = math.sin(t*8)*12
        col(c, "#ffffff"); c.move_to(72, -560); c.curve_to(120, -560+wv, 150, -540-wv, 200, -550+wv); c.line_to(200, -470+wv); c.curve_to(150, -460-wv, 120, -480+wv, 72, -480); c.close_path(); c.fill()
    elif gun:
        c.move_to(20, -300); c.line_to(80, -250); c.stroke()
        col(c, "#3a2a1a"); c.set_line_width(14); c.move_to(-20, -240); c.line_to(150, -300); c.stroke()
    else:
        aa = armup
        c.move_to(25, -300); c.line_to(55 + aa*20, -200 - aa*190 + math.sin(t*9)*aa*20); c.stroke()
    c.set_line_width(24); col(c, shirt)
    c.move_to(-25, -300); c.line_to(-50 - armup2*25, -200 - armup2*190 + math.sin(t*9+1)*armup2*20); c.stroke()
    # head
    if hair:
        col(c, hair); c.arc(0, -395, 58, PI*0.9, PI*2.1); c.fill(); rrect(c, -60, -400, 30, 110, 14); c.fill()
    col(c, skin); c.arc(0, -385, 52, 0, 2*PI); c.fill()
    if beard:
        col(c, "#5a3a1e"); c.arc(0, -365, 50, 0, PI); c.fill()
    col(c, "#000"); ell(c, 18, -392, 6, 8); c.fill()
    c.set_line_width(5)
    if sad: c.arc(15, -350, 16, PI*1.15, PI*1.85)
    else: c.arc(15, -368, 16, PI*0.15, PI*0.85)
    c.stroke()
    if mustache:
        col(c, "#4a2e18"); ell(c, 22, -362, 26, 9); c.fill()
    # hat
    if hat == "slouch":
        col(c, "#7a6a3a"); ell(c, 0, -425, 85, 18); c.fill(); c.arc(0, -430, 50, PI, 2*PI); c.fill()
        col(c, "#4a3f22"); c.rectangle(-50, -440, 100, 10); c.fill()
    elif hat == "straw":
        col(c, "#f2cd5c"); ell(c, 0, -425, 95, 20); c.fill(); c.arc(0, -432, 48, PI, 2*PI); c.fill()
        col(c, "#c0392b"); c.rectangle(-48, -442, 96, 10); c.fill()
    elif hat == "officer":
        col(c, "#5b6332"); rrect(c, -55, -470, 110, 45, 10); c.fill(); col(c, "#2b2b1a"); ell(c, 25, -425, 55, 10); c.fill()
        col(c, "#d63031"); c.rectangle(-55, -440, 110, 10); c.fill()
    elif hat == "bicorne":
        col(c, "#111111"); c.move_to(-110, -420); c.curve_to(-60, -520, 60, -520, 110, -420); c.curve_to(40, -445, -40, -445, -110, -420); c.close_path(); c.fill()
        col(c, "#1e4fa3"); c.arc(0, -455, 14, 0, 2*PI); c.fill(); col(c, "#ffffff"); c.arc(0, -455, 9, 0, 2*PI); c.fill(); col(c, "#d63031"); c.arc(0, -455, 4, 0, 2*PI); c.fill()
    elif hat == "bonnet":
        col(c, "#ffffff"); c.arc(0, -418, 56, PI*0.95, PI*2.05); c.fill(); c.rectangle(-58, -428, 116, 12); c.fill()
    elif hat == "beret":
        col(c, "#2d3e2a"); ell(c, -5, -432, 62, 22); c.fill(); col(c, "#d63031"); c.arc(25, -432, 7, 0, 2*PI); c.fill()
    elif hat == "pith":
        col(c, "#e8d8a8"); ell(c, 0, -425, 90, 16); c.fill(); c.arc(0, -430, 52, PI, 2*PI); c.fill()
        col(c, "#8b6f3a"); c.rectangle(-52, -438, 104, 8); c.fill()
    elif hat == "crown":
        col(c, "#f5c542"); c.move_to(-50, -425); c.line_to(-55, -490); c.line_to(-25, -455); c.line_to(0, -500); c.line_to(25, -455); c.line_to(55, -490); c.line_to(50, -425); c.close_path(); c.fill()
        col(c, "#e74c3c"); c.arc(0, -470, 8, 0, 2*PI); c.fill()
    elif hat == "sailor":
        col(c, "#ffffff"); ell(c, 0, -425, 62, 14); c.fill(); c.arc(0, -430, 46, PI, 2*PI); c.fill(); col(c, "#1e3a8a"); c.rectangle(-46, -438, 92, 8); c.fill()
    elif hat == "top":
        col(c, "#222222"); ell(c, 0, -425, 80, 14); c.fill(); c.rectangle(-45, -540, 90, 115); c.fill(); col(c, "#8b0000"); c.rectangle(-45, -445, 90, 14); c.fill()
    elif hat == "astro":
        col(c, "#dee2e6", 0.55); c.arc(0, -385, 82, 0, 2*PI); c.fill(); col(c, "#868e96"); c.set_line_width(8); c.arc(0, -385, 82, 0, 2*PI); c.stroke()
        col(c, "#ffffff", 0.6); ell(c, -30, -420, 18, 10); c.fill()
    elif hat == "cap":
        col(c, "#5f3dc4"); c.arc(0, -400, 54, PI, 2*PI); c.fill(); ell(c, 40, -402, 50, 10); c.fill()
    elif hat == "jester":
        for dx, cc in [(-1, "#d63031"), (1, "#f1c40f")]:
            col(c, cc); c.move_to(0, -425); c.line_to(dx*90, -500); c.line_to(dx*40, -430); c.close_path(); c.fill()
    c.restore()

def mgun(c, x, y, s=1, rot=0, flash=False):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.set_line_width(12); col(c, "#333"); c.set_line_cap(cairo.LINE_CAP_ROUND)
    for dx in (-70, 0, 70): c.move_to(0, -90); c.line_to(dx, 0); c.stroke()
    c.translate(0, -100); c.rotate(rot)
    col(c, "#2d3436"); rrect(c, -80, -28, 170, 56, 12); c.fill()
    col(c, "#636e72"); c.rectangle(80, -12, 140, 24); c.fill()
    col(c, "#1e272e"); ell(c, 0, -45, 45, 22); c.fill()
    if flash:
        col(c, "#ffd23f");
        c.move_to(225, 0)
        for i in range(10):
            a = i*PI/5; r = 55 if i % 2 == 0 else 22
            c.line_to(225+math.cos(a)*r, math.sin(a)*r)
        c.close_path(); c.fill()
    c.restore()

def wheat(c, x, y, h, t, ph=0, alpha=1):
    sway = math.sin(t*2 + ph)*0.08
    c.save(); c.translate(x, y); c.rotate(sway)
    col(c, "#c9a227", alpha); c.set_line_width(6); c.move_to(0, 0); c.line_to(0, -h); c.stroke()
    col(c, "#f1c40f", alpha)
    for i in range(5):
        ell(c, -9, -h + i*16, 8, 13); c.fill(); ell(c, 9, -h + i*16 + 8, 8, 13); c.fill()
    ell(c, 0, -h - 12, 7, 13); c.fill()
    c.restore()

def fence(c, x0, y, n, t, broken_from=999):
    for i in range(n):
        x = x0 + i*110
        if i >= broken_from:
            c.save(); c.translate(x, y); c.rotate(1.1 + (i % 2)*0.3); col(c, "#8b5a2b"); c.rectangle(-10, -130, 20, 130); c.fill(); c.restore()
        else:
            col(c, "#8b5a2b"); c.rectangle(x-10, y-130, 20, 130); c.fill()
    col(c, "#a0522d");
    if broken_from > n:
        c.rectangle(x0-10, y-110, (n-1)*110+20, 12); c.fill(); c.rectangle(x0-10, y-60, (n-1)*110+20, 12); c.fill()
    else:
        c.rectangle(x0-10, y-110, max(0, (broken_from-1))*110+20, 12); c.fill()

def truck(c, x, y, s, t, bounce=1):
    c.save(); c.translate(x, y + math.sin(t*25)*8*bounce); c.rotate(math.sin(t*17)*0.04*bounce); c.scale(s, s)
    col(c, "#556b2f"); rrect(c, -260, -230, 330, 150, 14); c.fill()
    col(c, "#6b8e23"); rrect(c, 70, -200, 150, 120, 16); c.fill()
    col(c, "#bde4ff"); rrect(c, 110, -185, 85, 55, 8); c.fill()
    for wx in (-170, 140):
        col(c, "#1e1e1e"); c.arc(wx, -70, 55, 0, 2*PI); c.fill(); col(c, "#888"); c.arc(wx, -70, 20, 0, 2*PI); c.fill()
    c.restore()
    mgun(c, x - 100*s, y - 230*s + math.sin(t*25)*8*bounce, s*0.8, rot=math.sin(t*13)*0.35*bounce, flash=(int(t*12) % 3 == 0))
    person(c, x - 190*s, y - 230*s + math.sin(t*25)*8*bounce, s*0.7, t, hat="slouch", gun=False, armup=0.0)

def dust(c, x, y, t, n=6, spread=1):
    for i in range(n):
        rnd = random.Random(i*7); ph = (t*1.5 + rnd.random()) % 1
        col(c, "#d9a066", 0.6*(1-ph)); c.arc(x - ph*160*spread + rnd.uniform(-20, 20), y - ph*60 - rnd.uniform(0, 40), 20 + ph*45, 0, 2*PI); c.fill()

def bullet_icon(c, x, y, s=1):
    c.save(); c.translate(x, y); c.scale(s, s)
    col(c, "#c8a03c"); rrect(c, -14, -20, 28, 70, 5); c.fill(); col(c, "#b87333"); c.move_to(-14, -20); c.curve_to(-14, -60, 14, -60, 14, -20); c.close_path(); c.fill()
    c.restore()

def chip(c, s, x, y, bg="#ff3b30", fg="#ffffff", size=50, a=1, sc=1):
    w = text_w(c, s, size) + size*1.1; h = size*1.6
    c.save(); c.translate(x, y); c.scale(sc, sc)
    col(c, "#000000", 0.25*a); rrect(c, -w/2+6, -h/2+8, w, h, h/2); c.fill()
    col(c, bg, a); rrect(c, -w/2, -h/2, w, h, h/2); c.fill(); c.restore()
    text(c, s, x, y, size*sc, fill=fg, stroke=None, alpha=a)

def stamp(c, s, x, y, p, size=150, colr="#e74c3c", rot=-0.2):
    if p <= 0: return
    sc = 1 + 2.5*(1-ease(p*3)) if p < 0.34 else 1
    a = min(1, p*4)
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(sc, sc)
    w = text_w(c, s, size) + 80
    c.set_line_width(14); col(c, colr, a); rrect(c, -w/2, -size*0.75, w, size*1.5, 24); c.stroke()
    c.restore()
    text(c, s, x, y, size*sc, fill=colr, stroke="#ffffff", sw=0.08, rot=rot, alpha=a)

def counter(c, x, y, val, label, size=130, p=1, colr="#ffd23f"):
    s = f"{int(val):,}".replace(",", ".")
    text(c, s, x, y, size*back(p), fill=colr, stroke="#111", sw=0.14)
    text(c, label, x, y + size*0.85, size*0.38*back(p), fill="#ffffff", stroke="#111", sw=0.18)



# ================= extra characters & props =================
def bear(c, x, y, s=1, t=0, walk=0, face=1, stand=False, carry=False, beer=False, salute=False, helmet=False, happy=True):
    c.save(); c.translate(x, y); c.scale(s*face, s)
    ph = t*walk*8; bob = abs(math.sin(ph))*8 if walk else 0
    c.translate(0, -bob)
    fur, dark, muz = "#8b5a2b", "#6b4423", "#d2a679"
    if not stand:
        for k, off in [(0, 0), (1, PI)]:
            a = math.sin(ph+off)*0.4 if walk else 0
            for bx in (-110, 110):
                col(c, dark if k else fur); c.save(); c.translate(bx + k*20, -110); c.rotate(a)
                rrect(c, -28, 0, 56, 115, 26); c.fill(); c.restore()
        col(c, fur); ell(c, 0, -170, 175, 105); c.fill()
        hx, hy = 165, -235
        if carry:
            col(c, "#7a5c2e"); rrect(c, -90, -330, 170, 90, 10); c.fill()
            col(c, "#5a4220"); c.rectangle(-90, -295, 170, 10); c.fill()
            bullet_icon(c, -40, -350, 1.1); bullet_icon(c, 0, -350, 1.1); bullet_icon(c, 40, -350, 1.1)
    else:
        col(c, dark)
        for bx in (-50, 50): rrect(c, bx-32, -150, 64, 150, 30); c.fill()
        col(c, fur); ell(c, 0, -280, 115, 165); c.fill()
        col(c, muz); ell(c, 0, -250, 70, 100); c.fill()
        hx, hy = 0, -470
        # arms
        c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_width(60); col(c, fur)
        if carry:
            c.move_to(-80, -360); c.line_to(-90, -520); c.stroke(); c.move_to(80, -360); c.line_to(90, -520); c.stroke()
            col(c, "#7a5c2e"); rrect(c, -130, -640, 260, 120, 12); c.fill(); col(c, "#5a4220"); c.rectangle(-130, -590, 260, 12); c.fill()
            text(c, "155 mm", 0, -580, 40, fill="#f5e6c8", stroke=None)
        elif salute:
            c.move_to(80, -360); c.line_to(150, -470); c.line_to(70, -520); c.stroke()
            c.move_to(-80, -360); c.line_to(-110, -230); c.stroke()
        elif beer:
            c.move_to(80, -360); c.line_to(130, -480); c.stroke(); c.move_to(-80, -360); c.line_to(-110, -230); c.stroke()
            bottle(c, 125, -500, 1.0, rot=-2.4 + math.sin(t*3)*0.15)
        else:
            c.move_to(80, -360); c.line_to(140 + math.sin(t*6)*20, -230); c.stroke(); c.move_to(-80, -360); c.line_to(-140, -230); c.stroke()
    # head
    col(c, fur); c.arc(hx-55, hy-75, 32, 0, 2*PI); c.fill(); c.arc(hx+55, hy-75, 32, 0, 2*PI); c.fill()
    col(c, muz); c.arc(hx-55, hy-75, 16, 0, 2*PI); c.fill(); c.arc(hx+55, hy-75, 16, 0, 2*PI); c.fill()
    col(c, fur); c.arc(hx, hy, 92, 0, 2*PI); c.fill()
    col(c, muz); ell(c, hx + (20 if not stand else 0), hy+30, 50, 38); c.fill()
    col(c, "#1e1e1e"); ell(c, hx + (20 if not stand else 0), hy+12, 18, 12); c.fill()
    bl = 0.15 if (t % 3.3) < 0.12 else 1
    ex = 20 if not stand else 0
    for d in (-32, 32):
        col(c, "#1e1e1e"); ell(c, hx + ex + d, hy-22, 10, 12*bl); c.fill()
        col(c, "#ffffff"); c.arc(hx + ex + d + 3, hy-26, 3.5, 0, 2*PI); c.fill()
    c.set_line_width(5); col(c, "#1e1e1e")
    if happy: c.arc(hx + ex, hy+40, 18, PI*0.15, PI*0.85)
    else: c.arc(hx + ex, hy+62, 18, PI*1.15, PI*1.85)
    c.stroke()
    if helmet or salute:
        col(c, "#2d3e2a"); ell(c, hx - 5, hy-80, 82, 26); c.fill(); col(c, "#d63031"); c.arc(hx + 30, hy-82, 9, 0, 2*PI); c.fill()
    c.restore()

def bottle(c, x, y, s=1, rot=0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    col(c, "#8b5a00"); rrect(c, -20, -40, 40, 90, 10); c.fill(); c.rectangle(-8, -75, 16, 40); c.fill()
    col(c, "#f5e6c8"); c.rectangle(-20, -10, 40, 30); c.fill(); c.restore()

def cigarette(c, x, y, s=1, rot=0, t=0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    col(c, "#ffffff"); c.rectangle(-60, -9, 100, 18); c.fill(); col(c, "#e67e22"); c.rectangle(-80, -9, 22, 18); c.fill()
    col(c, "#ff5722"); c.rectangle(40, -9, 8, 18); c.fill()
    for k in range(3):
        ph = (t*0.8 + k/3) % 1; col(c, "#bbbbbb", 0.6*(1-ph)); c.arc(55 + math.sin(ph*8)*12, -20 - ph*120, 10 + ph*18, 0, 2*PI); c.fill()
    c.restore()

def rabbit(c, x, y, s=1, t=0, hop=0, face=1, colr="#f0f0f0", ph0=0, angry=False):
    c.save(); c.translate(x, y); c.scale(s*face, s)
    ph = (t*hop*2.5 + ph0) % 1 if hop else 0
    jump = math.sin(ph*PI)*90 if hop else 0
    c.translate(0, -jump)
    inner = "#ffb6c1"
    col(c, colr); ell(c, 0, -70, 85, 65); c.fill()   # body
    ell(c, -70, -60, 30, 28); c.fill()               # tail
    col(c, "#ffffff"); c.arc(-80, -65, 22, 0, 2*PI); c.fill()
    col(c, colr); ell(c, 40, -10, 32, 14); c.fill()  # feet
    # head
    col(c, colr); c.arc(70, -140, 52, 0, 2*PI); c.fill()
    for dx, rt in [(-10, -0.25), (25, 0.15)]:
        c.save(); c.translate(55 + dx, -180); c.rotate(rt + math.sin(t*4 + dx)*0.08)
        col(c, colr); ell(c, 0, -70, 20, 72); c.fill(); col(c, inner); ell(c, 0, -70, 10, 55); c.fill(); c.restore()
    col(c, "#1e1e1e"); c.arc(92, -150, 9, 0, 2*PI); c.fill(); col(c, "#ffffff"); c.arc(95, -153, 3, 0, 2*PI); c.fill()
    col(c, "#ff8fab"); c.arc(120, -128, 9, 0, 2*PI); c.fill()
    if angry:
        c.set_line_width(6); col(c, "#1e1e1e"); c.move_to(78, -178); c.line_to(106, -166); c.stroke()
    c.restore()

def octopus(c, x, y, s=1, t=0, colr="#e8505b", face_mood="happy", show_hearts=False, swim=0, brains=False, blue=False, regrow=None, heart_on=(1,1,1)):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(8):
        a = -PI*0.05 + k*(PI*1.1/7)
        c.set_line_width(46 - 0*k); col(c, colr)
        x0, y0 = math.cos(a)*110, 60 + math.sin(a)*20
        c.move_to(x0, y0)
        pts = []
        nseg = 8 if (regrow is None or k != 7) else max(1, int(8*regrow))
        if regrow is not None and k == 7 and regrow < 0.13: continue
        for j in range(1, nseg + 1):
            r = 110 + j*38; ang = a + math.sin(t*3 + j*0.6 + k)*0.18 + swim*0.0
            pts.append((math.cos(ang)*r*0.9, 60 + j*42 + math.sin(t*3 + k + j)*10))
        for px, py in pts: c.line_to(px, py)
        c.stroke()
        if brains:
            px, py = pts[3]; col(c, "#ffd23f"); c.arc(px, py, 20 + 4*math.sin(t*6 + k), 0, 2*PI); c.fill()
    col(c, colr); ell(c, 0, -80, 175, 200); c.fill()
    col(c, "#ffffff", 0.18); ell(c, -60, -170, 50, 70); c.fill()
    for d in (-60, 60):
        col(c, "#ffffff"); ell(c, d, 0, 38, 42); c.fill(); col(c, "#1e1e1e"); c.arc(d + 8, 5, 18, 0, 2*PI); c.fill()
        col(c, "#ffffff"); c.arc(d + 14, -2, 6, 0, 2*PI); c.fill()
    c.set_line_width(7); col(c, "#7a1f27")
    if face_mood == "happy": c.arc(0, 50, 30, PI*0.15, PI*0.85); c.stroke()
    elif face_mood == "o": c.arc(0, 70, 16, 0, 2*PI); c.stroke()
    if brains:
        col(c, "#ffd23f"); c.arc(0, -150, 40 + 5*math.sin(t*6), 0, 2*PI); c.fill()
    if show_hearts:
        for k, (hx, hy, sc) in enumerate([(-90, -60, 0.6), (90, -60, 0.6), (0, -110, 0.8)]):
            beat = 1 + 0.15*max(0, math.sin(t*8 + k))
            if not heart_on[k]: heart(c, hx, hy, 60*sc, "#7f8c8d"); continue
            heart(c, hx, hy, 60*sc*beat, "#4a7bff" if blue else "#ff2e63")
    c.restore()

def heart(c, x, y, r, colr="#ff2e63"):
    c.save(); c.translate(x, y); col(c, colr)
    c.move_to(0, r*0.9); c.curve_to(-r*1.6, -r*0.2, -r*0.8, -r*1.4, 0, -r*0.5)
    c.curve_to(r*0.8, -r*1.4, r*1.6, -r*0.2, 0, r*0.9); c.close_path(); c.fill()
    col(c, "#ffffff", 0.35); c.arc(-r*0.45, -r*0.5, r*0.22, 0, 2*PI); c.fill(); c.restore()

def bee(c, x, y, s=1, t=0, face=1):
    c.save(); c.translate(x, y); c.scale(s*face, s)
    wing = abs(math.sin(t*40))
    col(c, "#ffffff", 0.75); ell(c, -10, -45, 30, 45*wing + 5); c.fill(); ell(c, 15, -45, 25, 40*wing + 5); c.fill()
    col(c, "#ffc312"); ell(c, 0, 0, 60, 40); c.fill()
    col(c, "#1e1e1e")
    for bx in (-25, 5): c.rectangle(bx, -38, 14, 76); c.fill()
    c.arc(55, -5, 26, 0, 2*PI); c.fill()
    col(c, "#ffffff"); c.arc(64, -12, 8, 0, 2*PI); c.fill(); col(c, "#1e1e1e"); c.arc(66, -12, 4, 0, 2*PI); c.fill()
    c.move_to(-60, 0); c.line_to(-82, 0); c.set_line_width(6); c.stroke()
    c.restore()

def honey_jar(c, x, y, s=1, t=0, level=1, ancient=False, label="MIEL"):
    c.save(); c.translate(x, y); c.scale(s, s)
    if ancient:
        col(c, "#b5651d"); c.move_to(-90, -300); c.curve_to(-170, -200, -150, -20, -80, 0); c.line_to(80, 0); c.curve_to(150, -20, 170, -200, 90, -300); c.close_path(); c.fill()
        col(c, "#8b4513"); rrect(c, -70, -340, 140, 50, 12); c.fill()
        col(c, "#1e1e1e", 0.6)
        for k in range(3): c.rectangle(-100, -230 + k*55, 200, 8); c.fill()
        col(c, "#ffb300"); ell(c, 0, -315, 60, 15); c.fill()
    else:
        col(c, "#ffffff", 0.35); rrect(c, -110, -300, 220, 300, 40); c.fill()
        hgt = 280*level
        col(c, "#ffb300"); rrect(c, -100, -10 - hgt, 200, hgt, 30); c.fill()
        col(c, "#ffd54f", 0.6); rrect(c, -80, -10 - hgt + 20, 30, max(10, hgt - 40), 12); c.fill()
        col(c, "#c0392b"); rrect(c, -100, -350, 200, 60, 14); c.fill()
        col(c, "#fff3c4"); rrect(c, -80, -200, 160, 80, 10); c.fill()
        text(c, label, 0, -160, 44, fill="#8b4513", stroke=None)
    c.restore()

def pyramid(c, x, y, w, h, colr="#e0b872", shade="#c39a55"):
    col(c, colr); c.move_to(x - w/2, y); c.line_to(x, y - h); c.line_to(x + w/2, y); c.close_path(); c.fill()
    col(c, shade); c.move_to(x, y - h); c.line_to(x + w/2, y); c.line_to(x + w*0.12, y); c.close_path(); c.fill()

def palm(c, x, y, s=1, t=0):
    c.save(); c.translate(x, y); c.scale(s, s)
    col(c, "#8b5a2b"); c.set_line_width(26); c.move_to(0, 0); c.curve_to(10, -120, -10, -220, 20, -330); c.stroke()
    col(c, "#2e8b57")
    for k in range(6):
        a = -PI/2 + (k-2.5)*0.55 + math.sin(t*2)*0.05
        c.save(); c.translate(20, -330); c.rotate(a); ell(c, 80, 0, 90, 22); c.fill(); c.restore()
    c.restore()

def ship(c, x, y, s=1, t=0):
    c.save(); c.translate(x, y + math.sin(t*2)*10); c.rotate(math.sin(t*1.6)*0.03); c.scale(s, s)
    col(c, "#5d6d7e"); c.move_to(-320, -80); c.line_to(320, -80); c.line_to(250, 40); c.line_to(-250, 40); c.close_path(); c.fill()
    col(c, "#ecf0f1"); c.rectangle(-150, -190, 260, 110); c.fill()
    col(c, "#34495e")
    for k in range(4): c.arc(-110 + k*60, -135, 14, 0, 2*PI); c.fill()
    col(c, "#c0392b"); c.rectangle(130, -280, 60, 200); c.fill(); col(c, "#1e1e1e"); c.rectangle(130, -280, 60, 25); c.fill()
    for k in range(3):
        ph = (t*0.6 + k/3) % 1; col(c, "#bdc3c7", 0.7*(1-ph)); c.arc(160 - ph*90, -300 - ph*200, 25 + ph*40, 0, 2*PI); c.fill()
    c.restore()

def sea(c, y, t, colr="#2e86de", colr2="#1b4f8a"):
    col(c, colr2); c.rectangle(-400, y, W + 800, H); c.fill()
    col(c, colr)
    c.move_to(-400, y)
    for k in range(40):
        xx = -400 + k*50; c.line_to(xx, y + math.sin(xx*0.02 + t*2)*14)
    c.line_to(W + 400, y + 60); c.line_to(-400, y + 60); c.close_path(); c.fill()

def underwater(c, t):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgba(0, *hexc("#48c6ef")); g.add_color_stop_rgba(1, *hexc("#0b3d91"))
    c.set_source(g); c.paint()
    for k in range(7):
        c.save(); c.translate(150 + k*150, -50); c.rotate(0.25 + math.sin(t*0.5 + k)*0.05)
        col(c, "#ffffff", 0.05); c.rectangle(-30, 0, 60, 2400); c.fill(); c.restore()
    rnd = random.Random(5)
    for k in range(25):
        bx = rnd.uniform(0, W); sp = rnd.uniform(60, 160); by = H - ((t*sp + rnd.uniform(0, H)) % H)
        col(c, "#ffffff", 0.35); c.arc(bx + math.sin(t*2 + k)*10, by, rnd.uniform(6, 16), 0, 2*PI); c.set_line_width(3); c.stroke()
    col(c, "#e6c88f"); c.move_to(-50, 1750)
    for k in range(25): c.line_to(-50 + k*50, 1730 + math.sin(k*0.9)*25)
    c.line_to(W + 50, H + 50); c.line_to(-50, H + 50); c.close_path(); c.fill()
    for k, (sx, hh) in enumerate([(120, 300), (900, 380), (980, 220), (60, 200)]):
        c.set_line_width(22); col(c, "#27ae60"); c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.move_to(sx, 1780)
        for j in range(1, 8): c.line_to(sx + math.sin(t*2 + j*0.8 + k)*25, 1780 - j*hh/7)
        c.stroke()

def night(c, t, top="#0b1a3a", bot="#3a2a6a"):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgba(0, *hexc(top)); g.add_color_stop_rgba(1, *hexc(bot)); c.set_source(g); c.paint()
    rnd = random.Random(9)
    for k in range(60):
        col(c, "#ffffff", 0.4 + 0.5*abs(math.sin(t*2 + k))); c.arc(rnd.uniform(0, W), rnd.uniform(0, 1100), rnd.uniform(1.5, 4), 0, 2*PI); c.fill()

def town(c, gy, t, wall="#f5deb3", roof="#8b3a2a", beams="#5a3a1e"):
    """medieval timber-frame houses"""
    for k in range(6):
        x = -60 + k*200; h = 360 + (k % 3)*70
        col(c, wall); c.rectangle(x, gy - h, 190, h); c.fill()
        col(c, beams); c.set_line_width(12)
        c.rectangle(x, gy - h, 190, h); c.stroke(); c.move_to(x, gy - h/2); c.line_to(x + 190, gy - h/2); c.stroke()
        c.move_to(x, gy - h); c.line_to(x + 190, gy - h/2); c.stroke()
        col(c, roof); c.move_to(x - 20, gy - h); c.line_to(x + 95, gy - h - 150); c.line_to(x + 210, gy - h); c.close_path(); c.fill()
        col(c, "#ffd27f"); c.rectangle(x + 40, gy - h + 60, 40, 50); c.fill(); c.rectangle(x + 110, gy - h + 60, 40, 50); c.fill()

def note_icon(c, x, y, s=1, colr="#ffffff", a=1):
    c.save(); c.translate(x, y); c.scale(s, s); col(c, colr, a)
    ell(c, 0, 0, 22, 16); c.fill(); c.rectangle(16, -90, 8, 90); c.fill(); c.move_to(24, -90); c.curve_to(60, -70, 50, -40, 40, -30); c.set_line_width(8); c.stroke(); c.restore()

def lute_player(c, x, y, s, t, shirt="#8e44ad", face=1):
    person(c, x, y, s, t, hat="jester", shirt=shirt, face=face)
    c.save(); c.translate(x + 40*s*face, y - 250*s); c.scale(s*face, s); c.rotate(-0.5)
    col(c, "#a0522d"); ell(c, 0, 0, 55, 70); c.fill(); col(c, "#5a3a1e"); c.rectangle(-8, -170, 16, 120); c.fill(); col(c, "#3e2412"); c.arc(0, -5, 16, 0, 2*PI); c.fill()
    c.restore()
    for k in range(3):
        ph = (t*0.7 + k/3) % 1; note_icon(c, x + 60*s*face + math.sin(ph*6 + k)*40, y - 450*s - ph*300, 0.8, "#ffffff", 1 - ph)

def carriage(c, x, y, s=1, t=0):
    c.save(); c.translate(x, y); c.scale(s, s)
    col(c, "#1e3d59"); rrect(c, -200, -330, 400, 230, 40); c.fill()
    col(c, "#f5c542"); c.set_line_width(10); rrect(c, -200, -330, 400, 230, 40); c.stroke()
    col(c, "#bde4ff"); rrect(c, -150, -300, 120, 100, 14); c.fill(); rrect(c, 30, -300, 120, 100, 14); c.fill()
    for wx in (-130, 130):
        col(c, "#5a3a1e"); c.arc(wx, -70, 70, 0, 2*PI); c.set_line_width(14); c.stroke()
        for k in range(6):
            a = k*PI/3 + t; c.move_to(wx, -70); c.line_to(wx + math.cos(a)*70, -70 + math.sin(a)*70); c.set_line_width(6); c.stroke()
    c.restore()

def grass_field(c, gy=1200, top="#87ceeb", bot="#e0f7ff", g1="#6ab04c", g2="#4e9a32"):
    sky(c, top, bot, g1, gy, g2)

def timeline(c, x0, x1, y, p, marks):
    """marks: list of (frac, label_top, label_bottom, colr)"""
    col(c, "#ffffff"); c.set_line_width(14); c.move_to(x0, y); c.line_to(x0 + (x1 - x0)*ease(p*1.5), y); c.stroke()
    for k, (f, lt, lb, cc) in enumerate(marks):
        if p*1.5 < f: continue
        xx = x0 + (x1 - x0)*f; pp = back((p*1.5 - f)*4)
        col(c, cc); c.arc(xx, y, 28*pp, 0, 2*PI); c.fill()
        text(c, lt, xx, y - 90, 56*pp, fill=cc); text(c, lb, xx, y + 90, 40*pp, fill="#ffffff")

def arrow(c, x0, y0, x1, y1, colr="#ffd23f", w=16):
    c.set_line_cap(cairo.LINE_CAP_ROUND); col(c, colr); c.set_line_width(w); c.move_to(x0, y0); c.line_to(x1, y1); c.stroke()
    a = math.atan2(y1 - y0, x1 - x0)
    c.move_to(x1 + math.cos(a)*20, y1 + math.sin(a)*20); c.line_to(x1 + math.cos(a + 2.5)*50, y1 + math.sin(a + 2.5)*50); c.line_to(x1 + math.cos(a - 2.5)*50, y1 + math.sin(a - 2.5)*50); c.close_path(); c.fill()

def radial_bg(c, t, c1, c2, rays=True):
    g = cairo.RadialGradient(540, 900, 50, 540, 900, 1300); g.add_color_stop_rgba(0, *hexc(c1)); g.add_color_stop_rgba(1, *hexc(c2))
    c.set_source(g); c.paint()
    if rays:
        for k in range(16):
            c.save(); c.translate(540, 950); c.rotate(k*PI/8 + t*0.3); col(c, "#ffffff", 0.06); c.move_to(0, 0); c.line_to(1500, -120); c.line_to(1500, 120); c.close_path(); c.fill(); c.restore()

def confetti(c, u, seed=1, n=70):
    rnd = random.Random(seed)
    for k in range(n):
        x = rnd.uniform(0, W); sp = rnd.uniform(200, 500); y = (rnd.uniform(0, H) + u*sp) % H
        col(c, rnd.choice(["#ffd23f", "#ffffff", "#00cec9", "#ff7675", "#55efc4"])); c.save(); c.translate(x, y); c.rotate(u*3 + k); c.rectangle(-10, -5, 20, 10); c.fill(); c.restore()


# ================= escenarios y personajes para las historias =================

# ---------- escenarios extra del canal "¿Qué pasaría si?" ----------
def stars(c, t, n=90, ymax=None, seed=11):
    rnd = random.Random(seed)
    for k in range(n):
        col(c, "#ffffff", 0.35 + 0.55*abs(math.sin(t*1.7 + k))); c.arc(rnd.uniform(0, W), rnd.uniform(0, ymax or H), rnd.uniform(1.5, 4.5), 0, 2*PI); c.fill()

def space_bg(c, t):
    g = cairo.RadialGradient(540, 800, 100, 540, 800, 1500); g.add_color_stop_rgba(0, *hexc("#1d2b64")); g.add_color_stop_rgba(1, *hexc("#070b1f"))
    c.set_source(g); c.paint(); stars(c, t)

def planet_earth(c, x, y, r, t, mood="sorpresa", face=True):
    """La Tierra como personaje: océano, continentes, ojos y boca. mood: sorpresa | feliz | triste | miedo"""
    col(c, "#4dabf7", 0.25); c.arc(x, y, r*1.12, 0, 2*PI); c.fill()
    c.save(); c.arc(x, y, r, 0, 2*PI); c.clip()
    col(c, "#1c7ed6"); c.paint()
    rot = (t*18) % (r*4)
    for k, (dx, dy, rx, ry) in enumerate([(-0.45, -0.35, 0.38, 0.26), (0.35, -0.5, 0.3, 0.2), (0.5, 0.25, 0.32, 0.38), (-0.3, 0.45, 0.4, 0.22), (-1.6, 0.0, 0.35, 0.3), (1.5, -0.1, 0.3, 0.42)]):
        cx = x + dx*r + rot*0.25
        if cx > x + r*1.6: cx -= r*3.2
        col(c, "#51cf66"); ell(c, cx, y + dy*r, rx*r, ry*r); c.fill()
        col(c, "#37b24d"); ell(c, cx + rx*r*0.25, y + dy*r + ry*r*0.25, rx*r*0.5, ry*r*0.45); c.fill()
    col(c, "#ffffff", 0.85); ell(c, x, y - r*0.98, r*0.55, r*0.12); c.fill(); ell(c, x, y + r*0.98, r*0.5, r*0.1); c.fill()
    col(c, "#000000", 0.18); c.arc(x + r*0.35, y + r*0.3, r*1.05, 0, 2*PI); c.set_line_width(r*0.35); c.stroke()
    c.restore()
    col(c, "#111111"); c.set_line_width(max(6, r*0.035)); c.arc(x, y, r, 0, 2*PI); c.stroke()
    if not face: return
    blink = 0.15 if (t % 3.2) < 0.12 else 1
    ey = y - r*0.12; eo = r*0.3
    for sx in (-1, 1):
        col(c, "#ffffff"); ell(c, x + sx*eo, ey, r*0.17, r*0.2*blink); c.fill()
        col(c, "#111111"); c.set_line_width(max(4, r*0.02)); ell(c, x + sx*eo, ey, r*0.17, r*0.2*blink); c.stroke()
        col(c, "#111111"); ell(c, x + sx*eo + r*0.03, ey + r*0.03, r*0.075, r*0.09*blink); c.fill()
        if mood in ("triste", "miedo"):
            c.set_line_width(max(5, r*0.03))
            c.move_to(x + sx*eo - sx*r*0.17, ey - r*0.3 - (0.06*r if mood == "triste" else 0))
            c.line_to(x + sx*eo + sx*r*0.15, ey - r*0.26 + (0.06*r if mood == "triste" else -0.08*r)); c.stroke()
    my = y + r*0.38
    col(c, "#111111")
    if mood == "feliz":
        c.set_line_width(max(6, r*0.04)); c.arc(x, my - r*0.12, r*0.22, PI*0.15, PI*0.85); c.stroke()
    elif mood == "triste":
        c.set_line_width(max(6, r*0.04)); c.arc(x, my + r*0.12, r*0.2, PI*1.15, PI*1.85); c.stroke()
        col(c, "#74c0fc"); ell(c, x + eo + r*0.05, ey + r*0.35 + (t*120 % (r*0.5)), r*0.04, r*0.06); c.fill()
    elif mood == "miedo":
        c.set_line_width(max(5, r*0.03)); c.move_to(x - r*0.2, my)
        for k in range(1, 9): c.line_to(x - r*0.2 + k*r*0.05, my + (r*0.04 if k % 2 else -r*0.04))
        c.stroke()
    else:
        ell(c, x, my, r*0.09, r*0.12*(0.85 + 0.15*math.sin(t*6))); c.fill()

def moon_ground(c, gy):
    col(c, "#adb5bd"); c.rectangle(0, gy, W, H); c.fill()
    rnd = random.Random(5)
    for k in range(14):
        x = rnd.uniform(0, W); y = rnd.uniform(gy + 60, H - 40); r = rnd.uniform(30, 90)
        col(c, "#868e96"); ell(c, x, y, r, r*0.3); c.fill(); col(c, "#ced4da"); ell(c, x, y - r*0.08, r*0.8, r*0.18); c.fill()

def tree(c, x, gy, s=1, t=0, ph=0):
    sw = math.sin(t*1.5 + ph)*0.03
    c.save(); c.translate(x, gy); c.rotate(sw); c.scale(s, s)
    col(c, "#8d5524"); c.rectangle(-22, -220, 44, 220); c.fill()
    for dx, dy, r, cc in [(0, -330, 130, "#2f9e44"), (-80, -260, 95, "#37b24d"), (85, -265, 100, "#40c057"), (0, -420, 90, "#51cf66")]:
        col(c, cc); c.arc(dx, dy, r, 0, 2*PI); c.fill()
    c.restore()

def colorful_city(c, gy, t, night_mode=False):
    cols = ["#f06595", "#ffd43b", "#63e6be", "#74c0fc", "#ff8787", "#b197fc", "#ffa94d"]
    for k in range(7):
        x = -30 + k*165; h = 520 + (k*173 % 330)
        col(c, cols[k % len(cols)]); c.rectangle(x, gy - h, 155, h); c.fill()
        col(c, "#111111"); c.set_line_width(6); c.rectangle(x, gy - h, 155, h); c.stroke()
        col(c, "#000000", 0.12); c.rectangle(x + 115, gy - h, 40, h); c.fill()
        for r in range(int((h - 60)/95)):
            for q in range(3):
                lit = (k*7 + r*3 + q) % 4 != 0
                col(c, ("#fff3bf" if lit else "#495057") if night_mode else "#e7f5ff"); c.rectangle(x + 16 + q*46, gy - h + 40 + r*95, 30, 48); c.fill()
                col(c, "#111111"); c.set_line_width(3); c.rectangle(x + 16 + q*46, gy - h + 40 + r*95, 30, 48); c.stroke()

def volcano(c, x, gy, w, h, t):
    col(c, "#6b4f3a"); c.move_to(x - w/2, gy); c.line_to(x - w*0.12, gy - h); c.line_to(x + w*0.12, gy - h); c.line_to(x + w/2, gy); c.close_path(); c.fill_preserve()
    col(c, "#111111"); c.set_line_width(6); c.stroke()
    col(c, "#ff6b00"); c.move_to(x - w*0.12, gy - h); c.line_to(x - w*0.06, gy - h*0.55); c.line_to(x, gy - h*0.75); c.line_to(x + w*0.05, gy - h*0.5); c.line_to(x + w*0.12, gy - h); c.close_path(); c.fill()
    for k in range(10):
        ph = (t*0.6 + k/10) % 1; rnd = random.Random(k)
        col(c, ["#868e96", "#adb5bd", "#495057"][k % 3], 0.9*(1 - ph)); c.arc(x + rnd.uniform(-60, 60) + ph*rnd.uniform(-160, 160), gy - h - ph*700, 50 + ph*120, 0, 2*PI); c.fill()

def room(c, t):
    col(c, "#ffe8cc"); c.rectangle(0, 0, W, 1250); c.fill()
    col(c, "#f4c99a")
    for k in range(0, W, 120): c.rectangle(k, 0, 8, 1250); c.fill()
    col(c, "#a5d8ff"); rrect(c, 640, 380, 320, 300, 20); c.fill(); col(c, "#ffffff"); c.set_line_width(18); rrect(c, 640, 380, 320, 300, 20); c.stroke()
    c.move_to(800, 380); c.line_to(800, 680); c.stroke(); c.move_to(640, 530); c.line_to(960, 530); c.stroke()
    col(c, "#a0522d"); c.rectangle(0, 1250, W, H); c.fill(); col(c, "#8b4513")
    for k in range(0, W, 180): c.rectangle(k, 1250, 6, H); c.fill()
    col(c, "#4263eb"); rrect(c, 90, 980, 420, 220, 50); c.fill(); col(c, "#364fc7"); rrect(c, 60, 1060, 480, 170, 40); c.fill()
    col(c, "#111111"); c.set_line_width(6); rrect(c, 60, 1060, 480, 170, 40); c.stroke()

FONDOS_EXTRA = ["marte", "espacio", "luna", "tierra", "ciudad_color", "ciudad_noche", "bosque", "playa", "volcan", "casa", "cielo", "oceano_profundo"]

def fondo_extra(c, nombre, t, mood=None):
    if nombre == "marte":
        sky(c, "#d9895b", "#f3c9a0", "#c1440e", 1250, "#9c360b"); col(c, "#fff4e0"); c.arc(820, 330, 45, 0, 2*PI); c.fill()
        for k in range(5):
            col(c, "#a33a0c"); x = 80 + k*230; ell(c, x, 1250, 160 + (k % 2)*60, 70 + (k % 3)*30); c.fill()
        return 1250
    if nombre == "espacio":
        space_bg(c, t); planet_earth(c, 260, 1650, 330, t, face=False); col(c, "#f1f3f5"); c.arc(880, 330, 70, 0, 2*PI); c.fill(); return 1250
    if nombre == "luna":
        space_bg(c, t); planet_earth(c, 820, 330, 130, t, face=False); moon_ground(c, 1250); return 1250
    if nombre == "tierra":
        space_bg(c, t); planet_earth(c, 540, 800 + math.sin(t*1.5)*12, 360, t, mood or "sorpresa"); return 1250
    if nombre in ("ciudad_color", "ciudad_noche"):
        if nombre == "ciudad_noche": night(c, t, "#0b1a3a", "#364fc7")
        else: sky(c, "#74c0fc", "#d0ebff", "#69db7c", 1250, "#51cf66"); cloud(c, 100, 250, 0.8); cloud(c, 650, 180, 0.6)
        colorful_city(c, 1250, t, nombre == "ciudad_noche")
        col(c, "#69db7c" if nombre == "ciudad_color" else "#2b8a3e"); c.rectangle(0, 1250, W, H); c.fill()
        col(c, "#111111"); c.set_line_width(6); c.move_to(0, 1250); c.line_to(W, 1250); c.stroke()
        return 1250
    if nombre == "bosque":
        sky(c, "#8ce99a", "#ebfbee", "#51cf66", 1250, "#40c057"); sun(c, 880, 300, 80, t)
        for k in range(6): tree(c, 40 + k*200, 1250 + (k % 2)*30, 1.1 + (k % 3)*0.15, t, k)
        return 1250
    if nombre == "playa":
        sky(c, "#74c0fc", "#e7f5ff", "#ffe066", 1300, "#fcc419"); sun(c, 850, 300, 85, t); cloud(c, 120, 300, 0.8)
        col(c, "#1c7ed6"); c.rectangle(0, 1080, W, 220); c.fill()
        col(c, "#ffffff", 0.7)
        for k in range(8): ell(c, (k*160 + t*40) % (W + 100) - 50, 1100 + (k % 3)*60, 50, 6); c.fill()
        palm(c, 120, 1320, 1.0, t); return 1300
    if nombre == "volcan":
        sky(c, "#ff8787", "#ffd8a8", "#5c3d2e", 1250, "#4a3226"); volcano(c, 540, 1250, 900, 650, t); return 1250
    if nombre == "casa":
        room(c, t); return 1250
    if nombre == "cielo":
        g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgba(0, *hexc("#4dabf7")); g.add_color_stop_rgba(1, *hexc("#e7f5ff")); c.set_source(g); c.paint()
        for k in range(9):
            rnd = random.Random(k); cloud(c, (rnd.uniform(-200, W) - t*rnd.uniform(30, 80)) % (W + 300) - 200, rnd.uniform(150, H - 200), rnd.uniform(0.7, 1.6))
        return 1500
    if nombre == "oceano_profundo":
        g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgba(0, *hexc("#1864ab")); g.add_color_stop_rgba(1, *hexc("#04102a")); c.set_source(g); c.paint()
        rnd = random.Random(4)
        for k in range(30):
            ph = (t*0.3 + rnd.random()) % 1; col(c, "#a5d8ff", 0.5*(1 - ph)); c.arc(rnd.uniform(0, W), H - ph*H, rnd.uniform(4, 14), 0, 2*PI); c.fill()
        return 1750
    return None

FONDOS = ["desierto", "campo", "pueblo", "pueblo_noche", "ciudad", "noche", "mar", "bajo_agua", "egipto", "nieve", "palacio", "laboratorio"]

def fondo(c, nombre, t, mood=None):
    """Dibuja el escenario. Devuelve la altura del suelo (y) donde van los personajes."""
    if nombre in FONDOS_EXTRA:
        return fondo_extra(c, nombre, t, mood)
    if nombre == "desierto":
        sky(c); sun(c, 860, 330, 90, t); cloud(c, 80, 260, 1); cloud(c, 560, 420, 0.7); return 1250
    if nombre == "campo":
        grass_field(c); sun(c, 880, 320, 85, t); cloud(c, 120, 300, 0.9); cloud(c, 600, 460, 0.6)
        for k in range(9): wheat(c, 40 + k*125, 1330, 160, t, k, 0.9)
        return 1250
    if nombre in ("pueblo", "pueblo_noche"):
        if nombre == "pueblo_noche": night(c, t)
        else: sky(c, "#9fd4f5", "#f6efe0", "#9e9e9e", 1250, "#8a8a8a"); cloud(c, 700, 260, 0.8)
        town(c, 1250, t)
        col(c, "#a59a8a"); c.rectangle(0, 1250, W, H); c.fill(); col(c, "#8d8270")
        for k in range(40):
            rnd = random.Random(k); ell(c, rnd.uniform(0, W), rnd.uniform(1270, H), rnd.uniform(30, 60), rnd.uniform(10, 18)); c.fill()
        return 1250
    if nombre == "ciudad":
        sky(c, "#a8d8ff", "#fdf0d5", "#7f8c8d", 1250, "#707b7c")
        for k in range(7):
            x = -40 + k*170; h = 420 + (k*137 % 300)
            col(c, ["#5d6d7e", "#85929e", "#34495e", "#a3b1c2"][k % 4]); c.rectangle(x, 1250 - h, 160, h); c.fill()
            col(c, "#fff3b0", 0.8)
            for r in range(int(h/90)):
                for q in range(3): c.rectangle(x + 20 + q*48, 1250 - h + 30 + r*90, 26, 40); c.fill()
        col(c, "#555"); c.rectangle(0, 1250, W, H); c.fill(); col(c, "#f5f5f5")
        for k in range(8): c.rectangle(k*150, 1560, 90, 16); c.fill()
        return 1250
    if nombre == "noche":
        night(c, t); col(c, "#f5f3ce"); c.arc(820, 330, 80, 0, 2*PI); c.fill()
        col(c, "#2c3e50"); c.rectangle(0, 1250, W, H); c.fill(); return 1250
    if nombre == "mar":
        sky(c, "#7fd3ff", "#e8f8ff", "#1b4f8a", 1150, "#1b4f8a"); sun(c, 850, 300, 80, t); cloud(c, 120, 280, 0.9)
        sea(c, 1150, t); return 1300
    if nombre == "bajo_agua":
        underwater(c, t); return 1750
    if nombre == "egipto":
        sky(c, "#8fd3fe", "#ffe9b5", "#e6c27a", 1250, "#d4a95c"); sun(c, 860, 300, 90, t)
        pyramid(c, 300, 1250, 520, 400); pyramid(c, 760, 1250, 380, 290); palm(c, 960, 1250, 0.9, t); return 1250
    if nombre == "nieve":
        sky(c, "#b9d7ea", "#f3f8fc", "#ffffff", 1250, "#e3edf5")
        rnd = random.Random(3)
        for k in range(70):
            x = rnd.uniform(0, W); y = (rnd.uniform(0, H) + t*rnd.uniform(40, 90)) % H
            col(c, "#ffffff", 0.9); c.arc(x + math.sin(t + k)*15, y, rnd.uniform(3, 8), 0, 2*PI); c.fill()
        return 1250
    if nombre == "palacio":
        col(c, "#7b2d26"); c.paint()
        for k in range(5):
            x = 60 + k*240; col(c, "#e8c872"); c.rectangle(x, 300, 70, 950); c.fill(); col(c, "#c9a54a"); c.rectangle(x - 15, 280, 100, 40); c.fill()
        col(c, "#b03a2e"); c.rectangle(300, 1250, 480, H); c.fill(); col(c, "#5b3a1e"); c.rectangle(0, 1250, 300, H); c.rectangle(780, 1250, 300, H); c.fill()
        return 1250
    if nombre == "laboratorio":
        g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgba(0, *hexc("#dff3f7")); g.add_color_stop_rgba(1, *hexc("#a7d7e0")); c.set_source(g); c.paint()
        col(c, "#ffffff"); c.rectangle(0, 1100, W, 40); c.fill(); col(c, "#7f8c8d"); c.rectangle(0, 1140, W, 110); c.fill()
        for k, cc in enumerate(["#55efc4", "#fd79a8", "#74b9ff", "#ffeaa7"]):
            x = 140 + k*240; col(c, cc, 0.85); c.move_to(x - 40, 1100); c.line_to(x + 40, 1100); c.line_to(x + 15, 1000); c.line_to(x + 15, 930); c.line_to(x - 15, 930); c.line_to(x - 15, 1000); c.close_path(); c.fill()
        col(c, "#dfe6e9"); c.rectangle(0, 1250, W, H); c.fill(); return 1250
    radial_bg(c, t, "#ffd98a", "#d9822b"); return 1250

PERSONAS = {
    "soldado": dict(hat="slouch", shirt="#6b7a3a", gun=True),
    "oficial": dict(hat="officer", shirt="#5b6332", mustache=True),
    "rey": dict(hat="crown", shirt="#8e1e3a", beard=True),
    "reina": dict(hat="crown", shirt="#6c3483", skirt="#4a235a", hair="#6d4c41"),
    "noble": dict(hat="top", shirt="#1e3d59", mustache=True),
    "cientifico": dict(hat="none", shirt="#fdfefe", hair="#bdc3c7"),
    "medico": dict(hat="none", shirt="#fdfefe", beard=True, hair="#5d4037"),
    "granjero": dict(hat="straw", shirt="#c0392b"),
    "marinero": dict(hat="sailor", shirt="#1e3a8a"),
    "explorador": dict(hat="pith", shirt="#c8a165"),
    "mujer": dict(hat="bonnet", shirt="#2980b9", skirt="#5d4037", hair="#6d4c41"),
    "hombre": dict(hat="none", shirt="#16a085", hair="#4a2e18"),
    "anciano": dict(hat="none", shirt="#7f8c8d", beard=True, hair="#ecf0f1"),
    "nino": dict(hat="none", shirt="#f39c12", hair="#4a2e18"),
    "general": dict(hat="bicorne", shirt="#1e3a8a"),
    "musico": dict(hat="jester", shirt="#8e44ad"),
    "atleta": dict(hat="none", shirt="#ffffff"),
    "astronauta": dict(hat="astro", shirt="#f1f3f5"),
    "chica": dict(hat="none", shirt="#4dabf7", hair="#5c3a21", skirt="#1864ab"),
    "chico": dict(hat="cap", shirt="#ff922b", hair="#3b2314"),
}
ANIMALES = {"emu", "oso", "conejo", "pulpo", "abeja"}
SHIRTS = ["#c0392b", "#2980b9", "#8e44ad", "#16a085", "#d35400", "#7f8c8d", "#27ae60"]

def _persona(c, nombre, x, y, s, t, k, accion, face):
    if nombre in ANIMALES:
        if nombre == "emu": emu(c, x, y, s, t, run=1 if accion == "correr" else 0, face=face, sad=accion == "triste")
        elif nombre == "oso": bear(c, x, y, s, t, walk=1 if accion in ("andar", "correr") else 0, face=face, happy=accion != "triste")
        elif nombre == "conejo": rabbit(c, x, y, s, t, hop=1 if accion in ("andar", "correr") else 0, face=face, ph0=k)
        elif nombre == "pulpo": octopus(c, x, y - 200*s, s, t)
        elif nombre == "abeja": bee(c, x, y - 300*s + math.sin(t*4 + k)*20, s*1.5, t, face=face)
        return
    kw = dict(PERSONAS.get(nombre, PERSONAS["hombre"]))
    if nombre in ("gente", "multitud") or kw is None: kw = {}
    walk = {"andar": 0.6, "correr": 1.2, "bailar": 0.6}.get(accion, 0)
    arm = {"celebrar": 1, "bailar": 0.5 + 0.5*math.sin(t*7 + k), "hablar": 0.4 + 0.3*math.sin(t*4 + k), "senalar": 0.6}.get(accion, 0)
    arm2 = {"celebrar": 1, "bailar": 0.5 + 0.5*math.sin(t*7 + k + 2)}.get(accion, 0)
    c.save()
    if accion == "bailar":
        c.translate(x, y); c.rotate(math.sin(t*5 + k)*0.12); c.translate(-x, -abs(math.sin(t*7 + k))*30*s)
    if accion == "tumbado":
        c.translate(x + 200*s, y - 40*s); c.rotate(-PI/2); c.translate(-x, -y)
    if "gun" in kw and accion in ("celebrar", "bailar"): kw.pop("gun")
    person(c, x, y, s, t + k, walk=walk, face=face, armup=arm if not kw.get("gun") else 0, armup2=arm2, sad=accion in ("triste", "tumbado"), **kw)
    c.restore()

def personajes(c, lista, gy, t, accion=None, seed=0):
    """lista: nombres de PERSONAS/ANIMALES, o 'gente'/'multitud' para un grupo. Se reparten por el suelo."""
    lista = list(lista or [])[:4]
    if not lista: return
    grupos = [n for n in lista if n in ("gente", "multitud")]
    solos = [n for n in lista if n not in ("gente", "multitud")]
    if grupos:
        n = 16 if "multitud" in grupos else 8; rnd = random.Random(seed); pos = []
        for k in range(n): pos.append((rnd.uniform(60, W - 60), gy + 220 + rnd.uniform(0, 1)*260, k))
        for x, y, k in sorted(pos, key=lambda z: z[1]):
            kw = dict(hat=rnd.choice(["none", "cap", "none", "none"]), shirt=SHIRTS[k % 7], hair=rnd.choice(["#3b2314", "#5c3a21", "#111111", "#c68642", None]))
            if k % 3 == 0: kw.update(hat="none", skirt=rnd.choice(["#1864ab", "#5f3dc4", "#c2255c"]), hair=rnd.choice(["#3b2314", "#5c3a21", "#e0a96d"]))
            c.save(); a = accion or "hablar"
            if a == "bailar": c.translate(0, -abs(math.sin(t*7 + k))*20)
            person(c, x, y, 0.5*(0.8 + (y - gy)/900), t + k, walk=0.6 if a in ("andar", "bailar", "correr") else 0,
                   armup=(0.5 + 0.5*math.sin(t*7 + k)) if a in ("bailar", "celebrar") else 0, sad=a == "triste", face=1 if k % 2 else -1, **kw)
            c.restore()
    n = len(solos)
    if not n: return
    xs = {1: [540], 2: [320, 760], 3: [220, 540, 860], 4: [160, 400, 680, 920]}[n]
    s = {1: 1.25, 2: 1.05, 3: 0.9, 4: 0.75}[n]
    y = min(H - 120, gy + 520)
    for k, (nm, x) in enumerate(zip(solos, xs)):
        face = 1 if x < 540 or n == 1 else -1
        _persona(c, nm, x, y, s, t, k, accion, face)
