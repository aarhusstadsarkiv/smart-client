## Smartarkivering - klient



### Api
- hent submission
  https://selvbetjening.aarhuskommune.dk/da/webform_rest/smartarkivering_test/submission/{submission_uuid}?api-key={api-key}

- hent filmetadata
  https://selvbetjening.aarhuskommune.dk/da/entity/file/{data.file_chooser[idx] from json-response to /submission/{submission_id} }?api-key={api-key}

- hent fildata
- {submission.data.linked.files.{key}.url}
  ..
    "linked": {
      "files": {
        "1274": {
          "id": "1274",
          "url": "https://selvbetjening.aarhuskommune.dk/system/files/webform/smartarkivering_test/{submission.sid}/1940-1950_indholdssider%20%C3%A5bne%20sager_2.txt",
          "mime_type": "text/plain",
          "size": "507790"
        }
      }
    }
