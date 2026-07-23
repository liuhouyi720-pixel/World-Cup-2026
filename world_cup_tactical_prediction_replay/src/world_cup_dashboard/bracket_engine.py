def advancing_team(prediction):
    return prediction.team_a if (prediction.team_a_advance or 0)>=(prediction.team_b_advance or 0) else prediction.team_b

