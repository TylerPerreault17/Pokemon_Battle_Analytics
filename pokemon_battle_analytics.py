"""
Pokemon Download Reader 
"""
### pip install beautifulsoup4
### pip install lxml

link = "Gen9NatDexDraft-2025-06-29-sword1101-umbrebro.html"
count = 4
pku = 0 
pko = 0 
pdofmon =  ["recoil", "sandstorm", "burn", "poison", "Flame Orb", 
            "Toxic Orb", "Rocky Helmet", "Sticky Barb", "Leech Seed", 
            "Salt Cure", "Pointed stones", "spikes",  "Magma Storm", 
            "Bind", "Whirlpool", "Wrap", "Sand Tomb", "Fire Spin",  
            "tormented", "liquid ooze", "lost some of its HP", 
            "afflicted by the curse", "perish count fell to 0",
            "Infestation", "hail", "Salt Cure"]
pdofomon = ["Aftermath", "Dry Skin", "Gulp Missile", "Iron Barbs",
            "Rough Skin", "Solar Power", "Explosion", "Memento", 
            "Self-Destruct", "Lunar Dance"] 
mon_user = ""
mon_opp = ""

from bs4 import BeautifulSoup
import pandas as pd

""" Who died """
def death(m, pko, pku):
    global kill_info
    if " fainted!" in m:
        m1 = m.split(" fainted!")
        nickname = m1[0]
        if ("The opposing") in m:
            m1 = nickname.split("The opposing ")
            nickname = m1[1]
            o = True
        else:
            o = False
        #print(f"{nickname} died")
        
        if pko >= 0 and o == True:
            ##print("passive kill of opponent")
            kill_info.loc[mon_user,"pko"] += 1
            kill_info.loc[mon_opp,"pdeath"] += 1
        
        elif pku >= 0 and o == False:
            ##print("passive kill of user")
            kill_info.loc[mon_user,"pdeath"] += 1
            kill_info.loc[mon_opp,"pko"] += 1
            
        elif o == True:
            ##print("direct kill of opponent")
            kill_info.loc[mon_user,"dko"] += 1
            kill_info.loc[mon_opp,"ddeath"] += 1
        
        else:
            ##print("direct kill of user")
            kill_info.loc[mon_user,"ddeath"] += 1
            kill_info.loc[mon_opp,"dko"] += 1

""" Who is actively in battle? """
def active_mon(m):
    global mon_opp
    global mon_user
    global kill_info
    
    team_u = kill_info.head(6)
    team_o = kill_info.tail(6)
    
    if "(" in m:
        if "sent out " in m:
            m1 = m.split(" sent out ")
            m2 = m1[1].split(" (")
            nickname = m2[0]
            m3 = m2[1].split(")!")
            mon = m3[0]
            ##print(f"---------{mon} - {nickname}")
            
            if( nickname not in kill_info["nick"].values):
                kill_info.loc[mon,"nick"] = nickname
                mon_opp = mon
            else:
                mon_opp = kill_info[kill_info["nick"]==nickname].index
            
        if "Go! " in m:
            m1 = m.split("Go! ")
            m2 = m1[1].split(" (")
            nickname = m2[0]
            m3 = m2[1].split(")!")
            mon = m3[0]
            #print(f"---------{mon} - {nickname}")
            
            if( nickname not in kill_info["nick"].values):
                kill_info.loc[mon,"nick"] = nickname
                mon_user = mon
            else:
                mon_user = kill_info[kill_info["nick"]==nickname].index
       
        if "dragged out" in m:
            m1 = m.split(" was dragged out!")
            m2 = m1[0].split(" (")
            nickname = m2[0]
            m3 = m2[1].split(")")
            mon = m3[0]
            if nickname in team_u.values:
                mon_user = kill_info[kill_info["nick"]==nickname].index
            else:
                if nickname in team_o.values:
                    mon_opp = kill_info[kill_info["nick"]==nickname].index
                elif mon in team_u.index:
                    kill_info.loc[mon,"nick"] = nickname
                    mon_user = mon
                else:
                    mon_opp = mon
                    kill_info.loc[mon,"nick"] = nickname
            
            
    elif "!" in m:
        if "sent out " in m:
            m1 = m.split(" sent out ")
            m2 = m1[1].split("!")
            mon = m2[0]
            nickname = mon
            ##print(f"---------{mon} - {nickname}")
            
            if( nickname not in kill_info["nick"].values):
                kill_info.loc[mon,"nick"] = nickname
                mon_opp = mon
            else:
                mon_opp = kill_info[kill_info["nick"]==nickname].index
        if "dragged out" in m:
            m1 = m.split(" was dragged out!")
            mon = m1[0]
            nickname = mon
            ##print(f"---------{mon} - {nickname}")
            
            if( nickname not in  kill_info["nick"].values):
                kill_info.loc[mon,"nick"] = nickname
            
                if(mon in team_u.index):
                    mon_user = mon
                if(mon in team_o.index):
                    mon_opp = mon
            
        if "Go! " in m:
            m1 = m.split("Go! ")
            m2 = m1[1].split("!")
            mon = m2[0]
            nickname = mon
            ##print(f"---------{mon} - {nickname}")
            
            if( nickname not in kill_info["nick"].values):
                kill_info.loc[mon,"nick"] = nickname
                mon_user = mon
            else:
                mon_user = kill_info[kill_info["nick"]==nickname].index
                
    
""" Passive kill potential countdoun"""
def passive_kill(m, pko, pku):
    ## Recall
    pko -= 1 
    pku -= 1
    for p in pdofmon: 
        if p in m:
            if "The opposing" in m:
                pko = count
            else:
                pku = count
            p = len(pdofmon)
    p = 0 
    for p in pdofomon:
        if p in m:
            if "The opposing" in m:
                pku = count
            else:
                pko = count 
            p = len(pdofomon)
        
    if "in its confusion" in m:
        if "The opposing" in m:
            pko = count
        else:
            pku = count
         
    elif ("Jaboca Berry" or "Rowap Berry") in m:
        if " hurt by the opposing " in m:
            pko = count
        else:
            pku = count
    
    
    elif("took its attacker down with it") in m:
        if "The opposing" in m:
            pku = count
        else:
            pko = count

    return pko, pku





"""Main"""

filename = open(link,"r") ## read only file

content1 = filename.read() ## html file to readable text form
##print(content) ##prints full html code, not cleaned
content = BeautifulSoup(content1, "lxml")
players = content.find_all("div", class_ = "chat battle-history")

battle_info = pd.DataFrame(columns=["Player","Mon1","Mon2","Mon3","Mon4","Mon5","Mon6"])

""" Split up the teams into mons and players, then add to main table"""
for p in players:
    ##print(p.text)
    team = p.text
    p1 = team.split("'s team: ")
        ##print(f"player = {p1[0]}")
    m = p1[1].split(" / ")
        ##print(m)
    pms = [p1[0], m[0], m[1], m[2], m[3], m[4], m[5]]
    battle_info = pd.concat([battle_info,pd.DataFrame([pms],columns=battle_info.columns)], ignore_index=True)

""" Setting up players """
player1 = battle_info.loc[0,"Player"]
player2 = battle_info.loc[1,"Player"]
battle_info = battle_info.set_index("Player")
print(battle_info)

""" Setting up mons initalizing pre-battle """
mp1 = battle_info.loc[player1,"Mon1"]
mp2 = battle_info.loc[player2,"Mon1"]

""" Separating out battle text """
mon_info = content.find_all("div", class_ = "battle-history")

""" checking battle text for information 
        - mons used, nicknames, forms
        - kills, deaths """
mons_all = [battle_info.loc[player1, "Mon1"], battle_info.loc[player1, "Mon2"], battle_info.loc[player1, "Mon3"],
            battle_info.loc[player1, "Mon4"], battle_info.loc[player1, "Mon5"], battle_info.loc[player1, "Mon6"],
            battle_info.loc[player2, "Mon1"], battle_info.loc[player2, "Mon2"], battle_info.loc[player2, "Mon3"],
            battle_info.loc[player2, "Mon4"], battle_info.loc[player2, "Mon5"], battle_info.loc[player2, "Mon6"]]
        
kill_info = pd.DataFrame(columns=["nick","dko","pko","ddeath","pdeath"], index = mons_all)
pd.set_option('future.no_silent_downcasting', True)
kill_info[["dko","pko","ddeath","pdeath"]] = kill_info[["dko","pko","ddeath","pdeath"]].fillna(0)

for m in  mon_info:
    #print(m.text)
    m = m.text
        
    ### finding mon / nickname values
    active_mon(m)
    pko, pku = passive_kill(m, pko, pku)
    death(m, pko, pku)
print("User Stats :")
print(kill_info.head(6))
print("\nOpp Stats :")
print(kill_info.tail(6))

user_death_sum = kill_info.iloc[0:6, :][["ddeath", "pdeath"]].sum().sum()
opp_death_sum = kill_info.iloc[6:, :][["ddeath", "pdeath"]].sum().sum()
##print(user_death_sum)
##print(opp_death_sum)

if(user_death_sum > 5):
    print("\nUser lost")
elif(opp_death_sum > 5):
    print("Opponent lost")
else:
    print("Game incomplete")


