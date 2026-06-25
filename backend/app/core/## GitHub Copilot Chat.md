## GitHub Copilot Chat

- Extension: 0.49.0 (prod)
- VS Code: 1.121.0 (f6cfa2ea2403534de03f069bdf160d06451ed282)
- OS: win32 10.0.26200 x64
- GitHub Account: javvadi-syamalagowri-lab

## Network

User Settings:
```json
  "http.systemCertificatesNode": true,
  "github.copilot.advanced.debug.useElectronFetcher": true,
  "github.copilot.advanced.debug.useNodeFetcher": false,
  "github.copilot.advanced.debug.useNodeFetchFetcher": true
```

Connecting to https://api.github.com:
- DNS ipv4 Lookup: Error (1347 ms): getaddrinfo ENOTFOUND api.github.com
- DNS ipv6 Lookup: timed out after 10 seconds
- Proxy URL: None (1 ms)
- Electron fetch (configured): timed out after 10 seconds
- Node.js https: timed out after 10 seconds
- Node.js fetch: Error (24 ms): TypeError: fetch failed
	at node:internal/deps/undici/undici:14902:13
	at process.processTicksAndRejections (node:internal/process/task_queues:103:5)
	at async n._fetch (c:\Users\jgowri\AppData\Local\Programs\Microsoft VS Code\f6cfa2ea24\resources\app\extensions\copilot\dist\extension.js:5484:5278)
	at async n.fetch (c:\Users\jgowri\AppData\Local\Programs\Microsoft VS Code\f6cfa2ea24\resources\app\extensions\copilot\dist\extension.js:5484:4590)
	at async u (c:\Users\jgowri\AppData\Local\Programs\Microsoft VS Code\f6cfa2ea24\resources\app\extensions\copilot\dist\extension.js:5516:186)
	at async Sg._executeContributedCommand (file:///c:/Users/jgowri/AppData/Local/Programs/Microsoft%20VS%20Code/f6cfa2ea24/resources/app/out/vs/workbench/api/node/extensionHostProcess.js:502:48807)
  Error: getaddrinfo ENOTFOUND api.github.com
  	at GetAddrInfoReqWrap.onlookupall [as oncomplete] (node:dns:122:26)
  	at GetAddrInfoReqWrap.callbackTrampoline (node:internal/async_hooks:130:17)

Connecting to https://api.githubcopilot.com/_ping:
- DNS ipv4 Lookup: Error (1 ms): getaddrinfo ENOTFOUND api.githubcopilot.com
- DNS ipv6 Lookup: timed out after 10 seconds
- Proxy URL: None (23 ms)
- Electron fetch (configured): Error (277 ms): Error: net::ERR_NETWORK_CHANGED
	at SimpleURLLoaderWrapper.<anonymous> (node:electron/js2c/utility_init:2:10684)
	at SimpleURLLoaderWrapper.emit (node:events:519:28)
	at SimpleURLLoaderWrapper.emit (node:domain:489:12)
	at SimpleURLLoaderWrapper.topLevelDomainCallback (node:domain:161:15)
	at SimpleURLLoaderWrapper.callbackTrampoline (node:internal/async_hooks:128:24)
  {"is_request_error":true,"network_process_crashed":false}
- Node.js https: 