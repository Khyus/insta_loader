from db import User, init_db
from sqlalchemy import text

session = init_db()

query = text(
'''
SELECT bio
FROM users
WHERE original_followers = True
ORDER BY id;
'''
)


user_list = ['kingsley_xm', 'dataslidsoftwares', 'dunmininuoluwar', 'meemie_lal', 'uniongraphic_design', 'penguin.8196546', 'nworiechinasagrace', 'arienzo_studio', 'rejoiceaml', 'oderapaparazzi', 'ayodele_dorcas_19', 'eminenceglobalproperties', 'michael_eminence', 'chicfitness2', 'spotglowdesign', 'aritradassharma', 'gbondo.francis', 'inkblend_branding', 'reemawadh9', 'de_nobletech', 'cute_siju05', 'bamigbolaololade', 'da_cyberkit', 'unknown_pearll', 'king___ahmadii', 'mickygrafix_design', 'mybrandpadi', 'hes.boy_styles', '_adegraphics', '__iamdavekeys', 'audububa_', 'igbkblack', 'traci_e_alcide', 'auta_graphix', 'paritie_studios', 'alobam_graphics001', 'peterbamigbola', 'wumxy_luxe', 'tasia_confentionaries', '2.folks', 'mira_essentials_store', 'daybreakstudios__', 'ab_d3signs', 'greengoddessshare', 'brainofcoco', 'nylahq__sofiar', 'natesam_lenz']




