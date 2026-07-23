import math

def normalize_probabilities(*values):
    values=[max(.00001,float(v)) for v in values]; total=sum(values); return tuple(v/total for v in values)
def outcome_probabilities(adv):
    draw=max(.18,min(.33,.29-abs(adv)*.08)); share=1-draw; a=share/(1+math.exp(-adv*4)); return normalize_probabilities(a,draw,share-a)
def scorelines(adv):
    la=max(.35,min(2.2,1.25+adv*.65)); lb=max(.35,min(2.2,1.25-adv*.65)); rows=[]
    for a in range(6):
        for b in range(6): rows.append({"score":f"{a}-{b}","probability":math.exp(-la)*la**a/math.factorial(a)*math.exp(-lb)*lb**b/math.factorial(b)})
    return sorted(rows,key=lambda x:x["probability"],reverse=True)[:5]

