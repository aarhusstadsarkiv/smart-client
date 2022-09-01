## Smartarkivering - klient


### Todo
- Config-setup skal nok erstattes af hardcodede værdier for de enkelte arkiver for at undgå at vise api-nøglen (med mindre nøglen roteres)


### Api
- hent submission
  https://selvbetjening.aarhuskommune.dk/da/webform_rest/smartarkivering_test/submission/{submission_uuid}?api-key={api-key}

- hent filmetadata
  https://selvbetjening.aarhuskommune.dk/da/entity/file/{data.file_chooser[idx] from json-response to /submission/{submission_id} }?api-key={api-key}

- hent fildata
  https://selvbetjening.aarhuskommune.dk/system/files/webform/smartarkivering_test/{submission.data.files[id]}/{filename}?api-key={api-key}