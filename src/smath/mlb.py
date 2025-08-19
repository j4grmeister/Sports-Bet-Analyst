def wOBA(NIBB, HBP, B1, B2, B3, HR, AB, BB, IBB, SF):
    """Calculate weighted on-base average.

    Parameters
    ----------
    NIBB : int
        Non-intentional bases on balls.
    HBP : int
        Hit by pitch.
    B1 : int
        Single.
    B2 : int
        Double.
    B3 : int
        Triple.
    HR : int
        Home run.
    AB : int
        At bat.
    BB : int
        Bases on balls.
    IBB : int
        Intentional bases on balls.
    SF : int
        Sacrifice flies.
    
    Returns
    -------
    float
        Weighted on-base average.
    """
    num = .697*NIBB + .727*HBP + .855*B1 + 1.248*B2 + 1.575*B3 + 2.014*HR
    den = AB + BB - IBB + SF + HBP
    if den == 0:
        return 0
    wOBA = num / den
    return wOBA

def OBP(H, BB, HBP, AB, SF):
    """Calculate on-base percentage.

    Parameters
    ----------
    H : int
        Hits.
    BB : int
        Bases on balls.
    HBP : int
        Hit by pitch.
    AB : int
        At bats.
    SF : int
        Sacrifice Flies.

    Returns
    -------
    float
        On-base percentage.
    """
    num = H + BB + HBP
    den = AB + BB + SF + HBP
    if den == 0:
        return 0
    OBP = num / den
    return OBP

def SLG(TB, AB):
    """Calculate slugging average.

    Parameters
    ----------
    TB : int
        Total bases.
    AB : int
        At bats.

    Returns
    -------
    float
        Slugging average.
    """
    if AB == 0:
        return 0
    SLG = TB / AB
    return SLG

def OPS(H, BB, HBP, AB, SF, TB):
    """Calculate on-base plus slugging.

    Parameters
    ----------
    H : int
        Hits.
    BB : int
        Bases on balls.
    HBP : int
        Hit by pitch.
    AB : int
        At bats.
    SF : int
        Sacrifice flies.
    TB : int
        Total bases.

    Returns
    -------
    float
        On-base plus slugging.
    """
    OPS = OBP(H, BB, HBP, AB, SF) + SLG(TB, AB)
    return OPS

def ERA(ER, IP):
    num = 9 * ER
    den = IP
    if den == 0:
        return 0
    ERA = num / den
    return ERA

def WHIP(BB, H, IP):
    num = (BB + H)
    den = IP
    if den == 0:
        return 0
    WHIP = num / den
    return WHIP

# Batting Average Against / Opponent Batting Average
def BAA(H, BF, BB, HBP, SH, SF, CINT):
    #TODO: Add SH and SF as tracked pitcher stats
    num = H
    den = BF - BB - HBP - SH - SF - CINT
    if den == 0:
        return 0
    BAA = num / den
    return BAA

def K9(K, IP):
    num = 9 * K
    den = IP
    if den == 0:
        return 0
    K9 = num / den
    return K9

def KBB(K, BB):
    if BB == 0:
        return 0
    KBB = K / BB
    return KBB