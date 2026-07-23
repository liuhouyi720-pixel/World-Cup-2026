import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

def xt_heatmap(profile,title=None):
    if not profile.vector or len(profile.vector)!=192:return None
    fig,ax=plt.subplots(figsize=(8,4.6)); im=ax.imshow(np.array(profile.vector).reshape(12,16),origin="lower",cmap="magma",aspect="auto"); ax.set_title(title or f"{profile.team} 历史 xT 威胁分布");ax.set_xlabel("向对方球门推进 →");ax.set_ylabel("球场宽度");fig.colorbar(im,ax=ax);fig.tight_layout();return fig

def difference_heatmap(a,b):
    if not a.vector or not b.vector:return None
    z=(np.array(a.vector)-np.array(b.vector)).reshape(12,16);limit=max(abs(z.min()),abs(z.max()));fig,ax=plt.subplots(figsize=(8,4.6));im=ax.imshow(z,origin="lower",cmap="RdBu_r",vmin=-limit,vmax=limit,aspect="auto");ax.set_title(f"{a.team} − {b.team} xT 分布差异");fig.colorbar(im,ax=ax);fig.tight_layout();return fig
