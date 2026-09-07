import requests
from bs4 import BeautifulSoup

# NOTE: The data will scrapped from these sites and saved as csv for further use. Once scrapped and saved, this part of code 
#  will not be called in later part of program implmentation

# Stats collected from Fifa's official website

# player related details 

# golden boot stats
golden_boot_uri = "https://gameday-prod.fifa.mangodev.co.uk/1-0/stories?query=(and%20resourceStatus==`urn:gd:resourceStatus:active`%20_externalId~`urn:gd:story:classification:gcp_top_scorer:competitionId:285023:(.*):rank_asc:page:2$`)&skip=0&limit=1&sort=tags.name==urn:gd:tag:story:fifa:column_number:asc"

# tags to extract = ["urn:gd:tag:football:stats:goals","urn:gd:tag:football:stats:assists","urn:gd:tag:football:stats:total_competition_minutes_played","urn:gd:tag:football:stats:fdcp_top_scorer_rank","urn:gd:tag:story:staff:position"]

# Attacking stats of players
attacking_uri = "https://gameday-prod.fifa.mangodev.co.uk/1-0/stories?query=(and%20resourceStatus==`urn:gd:resourceStatus:active`%20_externalId~`urn:gd:story:classification:gcp_attack:competitionId:285023:(.*):rank_asc:page:1$`)&skip=0&limit=1&sort=tags.name==urn:gd:tag:story:fifa:column_number:asc"
#tags to extract = ["urn:gd:tag:story:staff:rank","urn:gd:tag:football:stats:assists","urn:gd:tag:football:stats:attempt_at_goal_on_target","urn:gd:tag:football:stats:attempt_at_goal","urn:gd:tag:football:stats:attempt_at_goal_conversion_rate","urn:gd:tag:football:stats:attempt_at_goal_inside_the_penalty_area","urn:gd:tag:football:stats:attempt_at_goal_outside_the_penalty_area","urn:gd:tag:football:stats:headed_attempt_at_goal","urn:gd:tag:football:stats:corners"]

# distributiuon_stats
distribution_uri = "https://gameday-prod.fifa.mangodev.co.uk/1-0/stories?query=(and%20resourceStatus==`urn:gd:resourceStatus:active`%20_externalId~`urn:gd:story:classification:gcp_distribution:competitionId:285023:(.*):rank_asc:page:1$`)&skip=0&limit=1&sort=tags.name==urn:gd:tag:story:fifa:column_number:asc"

# defending_stats
defending_uri = "https://gameday-prod.fifa.mangodev.co.uk/1-0/stories?query=(and%20resourceStatus==`urn:gd:resourceStatus:active`%20_externalId~`urn:gd:story:classification:gcp_defending:competitionId:285023:(.*):rank_asc:page:1$`)&skip=0&limit=1&sort=tags.name==urn:gd:tag:story:fifa:column_number:asc"

# discipline_stats

# need tags for this
discipline_uri = "https://gameday-prod.fifa.mangodev.co.uk/1-0/stories?query=(and%20resourceStatus==`urn:gd:resourceStatus:active`%20_externalId~`urn:gd:story:classification:gcp_discipline:competitionId:285023:(.*):rank_asc:page:1$`)&skip=0&limit=1&sort=tags.name==urn:gd:tag:story:fifa:column_number:asc"

# goalkeeping_stats
goalkeeping_uri = "https://gameday-prod.fifa.mangodev.co.uk/1-0/stories?query=(and%20resourceStatus==`urn:gd:resourceStatus:active`%20_externalId~`urn:gd:story:classification:gcp_goalkeeping:competitionId:285023:(.*):rank_asc:page:1$`)&skip=0&limit=1&sort=tags.name==urn:gd:tag:story:fifa:column_number:asc"

# movement_stats
movement_uri = "https://gameday-prod.fifa.mangodev.co.uk/1-0/stories?query=(and%20resourceStatus==`urn:gd:resourceStatus:active`%20_externalId~`urn:gd:story:classification:gcp_movement:competitionId:285023:(.*):rank_asc:page:1$`)&skip=0&limit=1&sort=tags.name==urn:gd:tag:story:fifa:column_number:asc"

# physical_stats
# need stats for this
physical_uri = "https://gameday-prod.fifa.mangodev.co.uk/1-0/stories?query=(and%20resourceStatus==`urn:gd:resourceStatus:active`%20_externalId~`urn:gd:story:classification:gcp_physical:competitionId:285023:(.*):rank_asc:page:1$`)&skip=0&limit=1&sort=tags.name==urn:gd:tag:story:fifa:column_number:asc"



