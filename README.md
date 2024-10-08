## Smartarkivering

### GUI klient
En lille Gooey-baseret klient til hentning af afleveringer og tilhørende filer via Smartarkivering.dk's API.

Konfigurationsfilen ```config.json``` med endpoints og api-nøgle skal placeres i en mappe navngivet ``.smartarkivering`` (husk punktum) i roden af hver brugers Home-folder. Herved kan man styre præcis hvilke medarbejdere, der kan bruge programmet. Aktuelt ser konfigurationsfilen således ud:

```json
{
    "api_key": "[api-key-given-to-you]",
    "submission_url": "[endpoint-from-where-to-fetch-submissions-and-files]",
    "default_destination": "[default-path-to-dir-where-downloaded-files-are-to-be-stored]",
    "default_format": "[json|xml|arkibas]",
    "default_hash": "[md5|sha256]",
    "archive_prefix": "[archival-prefix-given-to-you]"
}
```

Seneste version af GUI-klienten kan til enhver tid hentes [her](https://github.com/aarhusstadsarkiv/smart-client/releases)

### Api
- submission-endpoint (payload indeholder også url'er til filer i `data.linked.files`)
  https://selvbetjening.aarhuskommune.dk/da/webform_rest/smartarkivering_test/submission/{submission_uuid}?api-key={api-key}

### Releases
Pyinstaller virker (indtil videre!) med følgende kald:

`poetry run pyinstaller --onefile --windowed --name smartarkivering .\smart_client\main.py`

Kaldet genererer en enkelt smartarkivering.exe fil, som ikke åbner et konsolvindue.

**NOTE:** Husk at man manuelt skal opdatere versionsnummeret i både pyproject.toml OG i gooey's 'program_name'-parameter 

### Hjemmeside
Fra smartarkivering.dk's forside kan der linkes til samme formular, men modtagende arkiv præ-udfyldt:

- [Kolding](https://selvbetjening.aarhuskommune.dk/da/content/smartarkivering?archive=kol)
- [Aalborg](https://selvbetjening.aarhuskommune.dk/da/content/smartarkivering?archive=aal)
- [Aarhus](https://selvbetjening.aarhuskommune.dk/da/content/smartarkivering?archive=aar)

Eller via det kommende smartarkivering.dk;

- [Kolding](https://aarhusstadsarkiv.github.io/smart-web/form?archive=kol)
- [Aalborg](https://aarhusstadsarkiv.github.io/smart-web/form?archive=aal)
- [Aarhus](https://aarhusstadsarkiv.github.io/smart-web/form?archive=aar)


**Man kan have alle felter præ-udfyldte, hvis man vil!**

Når man følger linket, bliver man redirected til Mitid, og efter login, videre til formularen. Man kan også benytte links'ne direkte fra andre sider/facebook-opslag m.v. Man skal bare huske at informere brugeren om, at de først bliver sendt til Mitid.
