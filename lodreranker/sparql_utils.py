filmtype_ids = ['Q11424', 'Q93204', 'Q226730', 'Q185529', 'Q200092', 'Q188473', 'Q24862', 'Q157443', 'Q319221', 'Q202866', 'Q219557', 'Q229390', 'Q506240', 'Q31235', 'Q645928', 'Q517386', 'Q842256', 'Q459290', 'Q1054574', 'Q369747', 'Q848512', 'Q24869', 'Q130232', 'Q959790', 'Q1067324', 'Q505119', 'Q652256', 'Q790192', 'Q1268687', 'Q1060398', 'Q12912091', 'Q2143665', 'Q663106', 'Q677466', 'Q336144', 'Q1935609', 'Q1146335', 'Q1200678', 'Q2165644', 'Q1361932', 'Q2484376', 'Q2973181', 'Q3250548', 'Q596138', 'Q2321734', 'Q2301591', 'Q1320115', 'Q430525', 'Q7130449', 'Q1251417', 'Q20442589', 'Q24865', 'Q3072043', 'Q3585697', 'Q917641', 'Q2125170', 'Q2903140', 'Q3677141', 'Q455315', 'Q3648909', 'Q370630', 'Q7858343', 'Q16909344']

def get_movie_query(element):

    filmtypes = ' '.join(f'wd:{x}' for x in filmtype_ids)

    q = """
        SELECT DISTINCT ?item
        WHERE   {
            ?item wdt:P31 ?type.
            ?item rdfs:label ?queryByTitle.
            ?item wikibase:sitelinks ?sitelinks
            VALUES ?type { """f'{filmtypes}'""" }
            FILTER(lang(?queryByTitle) = 'it')
            FILTER(REGEX(?queryByTitle, """f'"{element}"'""", "i"))
        }    
        ORDER BY DESC(?sitelinks) 
        LIMIT 1
        """
    return q
