import wikimapper as wikimapper

#wikimapper.download_wikidumps('hewiki-latest','./Data',overwrite=False)
wikimapper.create_index('hewiki-latest','./Data','./Output/Mapping')

mapper = wikimapper.WikiMapper("Output/Mapping")
wikidata_id = mapper.title_to_id("מתמטיקה"
print(wikidata_id) # Q28865