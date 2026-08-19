# RMI-Chat
> Proposta di progetto per il corso di Algoritmi distribuiti

## 1 Obiettivo
L’obiettivo del progetto è lo sviluppo di un’applicazione di chat basata su un’architettura client-server. Il server rappresenta il punto centralizzato di comunicazione tra i client e fornisce i servizi necessari alla gestione delle conversazioni, supportando sia chat private tra due utenti sia canali pubblici a cui possono partecipare più client contemporaneamente.
Ogni client potrà connettersi liberamente a uno dei server disponibili, consentendo all’utente di scegliere quello geograficamente più vicino e potenzialmente più efficiente in termini di latenza.

## 2 Topologia
Il sistema adotta una topologia asimmetrica basata su due tipologie di nodi: client e server. Il server rappresenta il nodo centrale che eroga il servizio di chat e costituisce l’unico punto di interazione attraverso cui i client possono comunicare all’interno della rete. Tutte le comunicazioni tra client avvengono quindi indirettamente tramite il server, che funge da intermediario e coordinatore delle interazioni.

## 3 Funzionamento
### 3.1 Server
Il server espone i seguenti servizi principali:
- richiesta della lista dei canali testuali disponibili;
- richiesta della lista degli utenti attualmente online;
- gestione dell’accesso e dell’uscita dai canali pubblici;
- gestione dell’accesso e dell’uscita dalle chat private;
- invio e ricezione di messaggi, sia nei canali pubblici sia nelle chat private.

Ogni client può essere connesso esclusivamente a un singolo contesto di comunicazione alla volta, ovvero a un canale pubblico oppure a una chat privata, ma non a entrambi simultaneamente.

## 3.2 Client
### 3.2.1 Stati
Ogni client può trovarsi in uno dei seguenti stati:
- Disconnected: il client non è connesso al server;
- InLobby: il client è connesso al server ma non partecipa a nessuna conversazione attiva;
- InChannel: il client è connesso a un canale pubblico;
- InPrivateChat: il client è impegnato in una chat privata con un altro utente.

### 3.2.2 Interfaccia
Il client espone un’interfaccia testuale che consente all’utente di eseguire le seguenti operazioni, organizzate in base allo stato corrente:
1. Connessione al server [Disconnected] → [InLobby]
    - il client tenta la connessione al server;
    - se il server non è disponibile o l’username scelto risulta già in uso, la connessione viene rifiutata;
    - in caso di successo, il server restituisce la lista dei canali disponibili e degli utenti attualmente in lobby.
2. Ingresso in un canale pubblico [InLobby] → [InChannel]
    - il client entra in un canale selezionato;
    - è possibile inviare e ricevere messaggi all’interno del canale;
    - il client può uscire dal canale tornando allo stato [InLobby].
3. Avvio di una chat privata [InLobby] → [InPrivateChat]
    - il client avvia una conversazione privata con un altro utente;
    - è possibile inviare e ricevere messaggi nella chat privata;
    - il client può terminare la chat tornando allo stato [InLobby].
4. Disconnessione dal server [InLobby] → [Disconnected]
