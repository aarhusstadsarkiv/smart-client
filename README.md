## Smartarkivering

### GUI klient
En lille Gooey-baseret klient til hentning af afleveringer og tilhørende filer via Smartarkivering.dk's API.

Konfigurationsfilen med endpoints og api-nøgle skal placeres i hver brugers Home-folder. Herved kan man styre præcis hvilke medarbejdere, der kan bruge programmet.

Der arbejdes med releases af .exe-filer. 

### Api
- submission-endpoint (payload indeholder også url'er til filer i `data.linked.files`)
  https://selvbetjening.aarhuskommune.dk/da/webform_rest/smartarkivering_test/submission/{submission_uuid}?api-key={api-key}

### Releases
Pyinstaller virker (indtil videre!) med følgende kald:

`pyinstaller --onefile --windowed --name smartarkivering .\smart_client\main.py`

Kaldet genererer en enkelt smartarkivering.exe fil, som ikke åbner et konsolvindue.

### Hjemmeside
Fra smartarkivering.dk's forside kan der linkes til samme formular, men modtagende arkiv præ-udfyldt:

- [Kolding](https://selvbetjening.aarhuskommune.dk/da/form/smartarkivering-test?archive=Kolding+Stadsarkiv)
- [Aalborg](https://selvbetjening.aarhuskommune.dk/da/form/smartarkivering-test?archive=Aalborg+Stadsarkiv)
- [Aarhus](https://selvbetjening.aarhuskommune.dk/da/form/smartarkivering-test?archive=Aarhus+Stadsarkiv)

Når man følger linket, bliver man redirected til Mitid, og efter login, videre til formularen. Man kan også benytte links'ne direkte fra andre sider/facebook-opslag m.v. Man skal bare huske at informere brugeren om, at de først bliver sendt til Mitid.
