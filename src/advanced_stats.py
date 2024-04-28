def ScPoss(tm_orb: int, fg_Part: float, ast_Part: float, ft_Part: float, tm_sc_poss: float, tm_orb_weight: float, tm_play_pct: float, orb_Part: float):
    return (fg_Part + ast_Part + ft_Part) * (1 - (tm_orb / tm_sc_poss) * tm_orb_weight * tm_play_pct) + orb_Part

def FG_Part(fgm: int, pts: int, ftm: int, fga: int, qAst: float):
    if fga == 0:
        return 0
    return fgm * (1 - 0.5 * ((pts - ftm) / (2 * fga)) * qAst)

def qAST(mp: int, tm_mp: int, tm_ast: int, ast: int, tm_fgm: int, fgm: int):
    if mp == 0:
        return 0
    return ((mp / (tm_mp / 5)) * (1.14 * ((tm_ast - ast) / tm_fgm))) + ((((tm_ast / tm_mp) * mp * 5 - ast) / ((tm_fgm / tm_mp) * mp * 5 - fgm)) * (1 - (mp / (tm_mp / 5))))

def AST_Part(tm_pts: int, tm_ftm: int, pts: int, ftm: int, tm_fga: int, ast: int, fga: int):
    return 0.5 * (((tm_pts - tm_ftm) - (pts - ftm)) / (2 * (tm_fga - fga))) * ast

def FT_Part(ftm: int, fta: int):
    if fta == 0:
        return 0
    return (1 - (1 - (ftm / fta)) ** 2) * 0.4 * fta

def Team_Scoring_Poss(tm_fgm: int, tm_ftm: int, tm_fta: int):
    return tm_fgm + (1 - (1 - (tm_ftm / tm_fta)) ** 2) * tm_fta * 0.4

def Team_ORB_Weight(tm_orb_pct: float, tm_play_pct: float):
    return ((1 - tm_orb_pct) * tm_play_pct) / ((1 - tm_orb_pct) * tm_play_pct + tm_orb_pct * (1 - tm_play_pct))

def Team_ORB_pct(tm_orb: int, opp_trb: int, opp_orb: int):
    return tm_orb / (tm_orb + (opp_trb - opp_orb))

def Team_Play_pct(tm_sc_poss: float, tm_fga: int, tm_fta: int, tm_tov: int):
    return tm_sc_poss / (tm_fga + tm_fta * 0.4 + tm_tov)

def ORB_Part(orb: int, tm_orb_weight: float, tm_play_pct: float):
    return orb * tm_orb_weight * tm_play_pct

def FGxPoss(fga: int, fgm: int, tm_orb_pct: float):
    return (fga - fgm) * (1 - 1.07 * tm_orb_pct)

def FTxPoss(ftm: int, fta: int):
    if fta == 0:
        return 0
    return ((1 - (ftm / fta)) ** 2) * 0.4 * fta

def TotPoss(sc_poss: float, fg_poss: float, ft_poss: float, tov: int):
    return sc_poss + fg_poss + ft_poss + tov

def PProd(p_prod_fg_part: float, p_prod_ast_part: float, ftm: int, tm_orb: int, tm_sc_poss: float, tm_orb_weight: float, tm_play_pct: float, p_prod_orb_part: float):
    return (p_prod_fg_part + p_prod_ast_part + ftm) * (1 - (tm_orb / tm_sc_poss) * tm_orb_weight * tm_play_pct) + p_prod_orb_part

def PProd_FG_Part(fgm: int, pm3: int, pts: int, ftm: int, fga: int, qAst: float):
    if fga == 0:
        return 0
    return 2 * (fgm + 0.5 * pm3) * (1 - 0.5 * ((pts - ftm) / (2 * fga)) * qAst)

def PProd_AST_Part(tm_fgm: int, fgm: int, tm_pm3: int, pm3: int, tm_pts: int, tm_ftm: int, pts: int, ftm: int, tm_fga: int, fga: int, ast: int):
    return 2 * ((tm_fgm - fgm + 0.5 * (tm_pm3 - pm3)) / (tm_fgm - fgm)) * 0.5 * (((tm_pts - tm_ftm) - (pts - ftm)) / (2 * (tm_fga - fga))) * ast

def PProd_ORB_Part(orb: int, tm_orb_weight: float, tm_play_pct: float, tm_pts: int, tm_fgm: int, tm_ftm: int, tm_fta: int):
    return orb * tm_orb_weight * tm_play_pct * (tm_pts / (tm_fgm + (1 - (1 - (tm_ftm / tm_fta)) ** 2) * 0.4 * tm_fta))

def Stops1(stl: int, blk: int, f_mut: float, dor_pct: float, drb: int):
    return stl + blk * f_mut * (1 - 1.07 * dor_pct) + drb * (1 - f_mut)

def FMut(dfg_pct: float, dor_pct: float):
    return (dfg_pct * (1 - dor_pct)) / (dfg_pct * (1 - dor_pct) + (1 - dfg_pct) * dor_pct)

def DOR_pct(opp_orb: int, tm_drb: int):
    return opp_orb / (opp_orb + tm_drb)

def DFG_pct(opp_fgm: int, opp_fga: int):
    return opp_fgm / opp_fga

def Stops2(opp_fga: int, opp_fgm: int, tm_blk: int, tm_mp: int, f_mut: float, dor_pct: float, opp_tov: int, tm_stl: int, mp: int, pf: int, tm_pf: int, opp_fta: int, opp_ftm: int):
    return (((opp_fga - opp_fgm - tm_blk) / tm_mp) * f_mut * (1 - 1.07 * dor_pct) + ((opp_tov - tm_stl) / tm_mp)) * mp + (pf / tm_pf) * 0.4 * opp_fta * (1 - (opp_ftm / opp_fta)) ** 2

def Stops(stops1: float, stops2: float):
    return stops1 + stops2

def Stop_pct(stops: float, opp_mp: int, tm_poss: float, mp):
    if mp == 0:
        return 0
    return (stops * opp_mp) / (tm_poss * mp)

def D_Pts_per_ScPoss(opp_pts: int, opp_fgm: int, opp_ftm: int, opp_fta: int):
    return opp_pts / (opp_fgm + (1 - (1 - (opp_ftm / opp_fta)) ** 2) * opp_fta * 0.4)

def poss(tm_fga: int, tm_fta: int, tm_orb: int, opp_drb: int, tm_fgm: int, tm_tov: int, opp_fga: int, opp_fta: int, opp_orb: int, tm_drb: int, opp_fgm: int, opp_tov: int):
    return 0.5 * ((tm_fga + 0.4 * tm_fta - 1.07 * (tm_orb / (tm_orb + opp_drb)) * (tm_fga - tm_fgm) + tm_tov) + (opp_fga + 0.4 * opp_fta - 1.07 * (opp_orb / (opp_orb + tm_drb)) * (opp_fga - opp_fgm) + opp_tov))
#---------------------------------------------------------------------
# final functions
def team_defensive_rating(opp_pts: int, tm_poss: float):
    return 100 * (opp_pts / tm_poss)

def offensive_rating(p_prod: float, tot_poss: float):
    if tot_poss == 0:
        return 0
    return 100 * (p_prod / tot_poss)

def defensive_rating(tm_def_rating: float, d_pts_per_sc_poss: float, stop_pct: float):
    return tm_def_rating + 0.2 * (100 * d_pts_per_sc_poss * (1 - stop_pct) - tm_def_rating)

def Floor_pct(sc_poss: float, tot_poss: float):
    if tot_poss == 0:
        return 0
    return sc_poss / tot_poss

def calculate_player_advanced_stats(player_stats: dict, team_offense_stats: dict, team_defensive_stats: dict):
    # player stats needed
    fgm = player_stats['FGM']
    fga = player_stats['FGA']
    pm3 = player_stats['3PM']
    ftm = player_stats['FTM']
    fta = player_stats['FTA']
    ast = player_stats['AST']
    orb = player_stats['ORB']
    drb = player_stats['DRB']
    stl = player_stats['STL']
    blk = player_stats['BLK']
    tov = player_stats['TOV']
    pf = player_stats['PF']
    pts = player_stats['PTS']
    mp = player_stats['MP']

    # team stats needed
    tm_fgm = team_offense_stats['FGM']
    tm_fga = team_offense_stats['FGA']
    tm_pm3 = team_offense_stats['3PM']
    tm_ftm = team_offense_stats['FTM']
    tm_fta = team_offense_stats['FTA']
    tm_ast = team_offense_stats['AST']
    tm_orb = team_offense_stats['ORB']
    tm_drb = team_offense_stats['DRB']
    tm_stl = team_defensive_stats['STL']
    tm_blk = team_defensive_stats['BLK']
    tm_tov = team_offense_stats['TOV']
    tm_pf = team_offense_stats['PF']
    tm_pts = team_offense_stats['PTS']
    tm_mp = team_offense_stats['MP']

    # oppnant stats needed
    opp_pts = team_defensive_stats['PTS']
    opp_fgm = team_defensive_stats['FGM']
    opp_fga = team_defensive_stats['FGA']
    opp_ftm = team_defensive_stats['FTM']
    opp_fta = team_defensive_stats['FTA']
    opp_trb = team_defensive_stats['TRB']
    opp_orb = team_defensive_stats['ORB']
    opp_drb = team_defensive_stats['DRB']
    opp_tov = team_defensive_stats['TOV']
    opp_mp = team_defensive_stats['MP']



    advanced_stats = {}

    # filter stats
    tm_orb_pct = Team_ORB_pct(tm_orb, opp_trb, opp_orb)
    qAst = qAST(mp, tm_mp, tm_ast, ast, tm_fgm, fgm)
    fg_Part = FG_Part(fgm, pts, ftm, fga, qAst)
    ast_Part = AST_Part(tm_pts, tm_ftm, pts, ftm, tm_fga, ast, fga)
    ft_Part = FT_Part(ftm, fta)
    tm_sc_poss = Team_Scoring_Poss(tm_fgm, tm_ftm, tm_fta)
    tm_play_pct = Team_Play_pct(tm_sc_poss, tm_fga, tm_fta, tm_tov)
    tm_orb_weight = Team_ORB_Weight(tm_orb_pct, tm_play_pct)
    orb_Part = ORB_Part(orb, tm_orb_weight, tm_play_pct)
    ft_poss = FTxPoss(ftm, fta)
    fg_poss = FGxPoss(fga, fgm, tm_orb_pct)
    sc_poss = ScPoss(tm_orb, fg_Part, ast_Part, ft_Part, tm_sc_poss, tm_orb_weight, tm_play_pct, orb_Part)
    tot_poss = TotPoss(sc_poss, fg_poss, ft_poss, tov)
    p_prod_fg_part = PProd_FG_Part(fgm, pm3, pts, ftm, fga, qAst)
    p_prod_ast_part = PProd_AST_Part(tm_fgm, fgm, tm_pm3, pm3, tm_pts, tm_ftm, pts, ftm, tm_fga, fga, ast)
    p_prod_orb_part = PProd_ORB_Part(orb, tm_orb_weight, tm_play_pct, tm_pts, tm_fgm, tm_ftm, tm_fta)
    p_prod = PProd(p_prod_fg_part, p_prod_ast_part, ftm, tm_orb, tm_sc_poss, tm_orb_weight, tm_play_pct, p_prod_orb_part)
    tm_poss = poss(tm_fga, tm_fta, tm_orb, opp_drb, tm_fgm, tm_tov, opp_fga, opp_fta, opp_orb, tm_drb, opp_fgm, opp_tov)
    tm_def_rating = team_defensive_rating(opp_pts, tm_poss)
    d_pts_per_sc_poss = D_Pts_per_ScPoss(opp_pts, opp_fgm, opp_ftm, opp_fta)
    dfg_pct = DFG_pct(opp_fgm, opp_fga)
    dor_pct = DOR_pct(opp_orb, tm_drb)
    f_mut = FMut(dfg_pct, dor_pct)
    stops1 = Stops1(stl, blk, f_mut, dor_pct, drb)
    stops2 = Stops2(opp_fga, opp_fgm, tm_blk, tm_mp, f_mut, dor_pct, opp_tov, tm_stl, mp, pf, tm_pf, opp_fta, opp_ftm)
    stops = Stops(stops1, stops2)
    stop_pct = Stop_pct(stops, opp_mp, tm_poss, mp)

    # final stats 
    oRtg = offensive_rating(p_prod, tot_poss)
    floor_pct = Floor_pct(sc_poss, tot_poss)
    dRtg = defensive_rating(tm_def_rating, d_pts_per_sc_poss, stop_pct)
    nRtg = oRtg - dRtg

    # added them in a dict
    advanced_stats['oRtg'] = oRtg
    advanced_stats['floor_pct'] = floor_pct
    advanced_stats['dRtg'] = dRtg
    advanced_stats['nRtg'] = nRtg
    return advanced_stats



# fgm = 406
# fga = 614
# pm3 = 0
# ftm = 249
# fta = 390
# ast = 102
# orb = 285
# drb = 697
# stl = 52
# blk = 162
# tov = 118
# pf = 238
# pts = 1061
# mp = 2588

# # team stats needed
# tm_fgm = 3383
# tm_fga = 6974
# tm_pm3 = 1037
# tm_ftm = 1461
# tm_fta = 1881
# tm_ast = 2184
# tm_orb = 770
# tm_drb = 2807
# tm_stl = 647
# tm_blk = 497
# tm_tov = 1095
# tm_pf = 1544
# tm_pts = 9264
# tm_mp = 19805

# # oppnant stats needed
# opp_pts = 8735
# opp_fgm = 3198
# opp_fga = 7114
# opp_ftm = 1402
# opp_fta = 1794
# opp_trb = 3398
# opp_orb = 843
# opp_drb = 2555
# opp_tov = 1113
# opp_mp = 19805



# advanced_stats = {}

# # filter stats
# tm_orb_pct = Team_ORB_pct(tm_orb, opp_trb, opp_orb)
# qAst = qAST(mp, tm_mp, tm_ast, ast, tm_fgm, fgm)
# fg_Part = FG_Part(fgm, pts, ftm, fga, qAst)
# ast_Part = AST_Part(tm_pts, tm_ftm, pts, ftm, tm_fga, ast, fga)
# ft_Part = FT_Part(ftm, fta)
# tm_sc_poss = Team_Scoring_Poss(tm_fgm, tm_ftm, tm_fta)
# tm_play_pct = Team_Play_pct(tm_sc_poss, tm_fga, tm_fta, tm_tov)
# tm_orb_weight = Team_ORB_Weight(tm_orb_pct, tm_play_pct)
# orb_Part = ORB_Part(orb, tm_orb_weight, tm_play_pct)
# ft_poss = FTxPoss(ftm, fta)
# fg_poss = FGxPoss(fga, fgm, tm_orb_pct)
# sc_poss = ScPoss(tm_orb, fg_Part, ast_Part, ft_Part, tm_sc_poss, tm_orb_weight, tm_play_pct, orb_Part)
# tot_poss = TotPoss(sc_poss, fg_poss, ft_poss, tov)
# p_prod_fg_part = PProd_FG_Part(fgm, pm3, pts, ftm, fga, qAst)
# p_prod_ast_part = PProd_AST_Part(tm_fgm, fgm, tm_pm3, pm3, tm_pts, tm_ftm, pts, ftm, tm_fga, fga, ast)
# p_prod_orb_part = PProd_ORB_Part(orb, tm_orb_weight, tm_play_pct, tm_pts, tm_fgm, tm_ftm, tm_fta)
# p_prod = PProd(p_prod_fg_part, p_prod_ast_part, ftm, tm_orb, tm_sc_poss, tm_orb_weight, tm_play_pct, p_prod_orb_part)
# tm_poss = poss(tm_fga, tm_fta, tm_orb, opp_drb, tm_fgm, tm_tov, opp_fga, opp_fta, opp_orb, tm_drb, opp_fgm, opp_tov)
# tm_def_rating = team_defensive_rating(opp_pts, tm_poss)
# d_pts_per_sc_poss = D_Pts_per_ScPoss(opp_pts, opp_fgm, opp_ftm, opp_fta)
# dfg_pct = DFG_pct(opp_fgm, opp_fga)
# dor_pct = DOR_pct(opp_orb, tm_drb)
# f_mut = FMut(dfg_pct, dor_pct)
# stops1 = Stops1(stl, blk, f_mut, dor_pct, drb)
# stops2 = Stops2(opp_fga, opp_fgm, tm_blk, tm_mp, f_mut, dor_pct, opp_tov, tm_stl, mp, pf, tm_pf, opp_fta, opp_ftm)
# stops = Stops(stops1, stops2)
# stop_pct = Stop_pct(stops, opp_mp, tm_poss, mp)

# # final stats 
# oRtg = offensive_rating(p_prod, tot_poss)
# floor_pct = Floor_pct(sc_poss, tot_poss)
# dRtg = defensive_rating(tm_def_rating, d_pts_per_sc_poss, stop_pct)
# print(dRtg)