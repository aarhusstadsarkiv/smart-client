## Smartarkivering - GUI klient
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