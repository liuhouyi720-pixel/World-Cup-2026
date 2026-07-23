from .xt_style_service import XTStyleService

class StrengthService:
    def __init__(self, xt: XTStyleService): self.xt = xt
    def score(self, team):
        p = self.xt.profile(team)
        if p.data_available: return (p.spatial["attacking_third_share"]-.70)*.35, "historical_xT_proxy"
        return 0., "global_neutral_fallback"

