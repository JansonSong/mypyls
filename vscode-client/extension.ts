import * as vscode from 'vscode';
import {LanguageClient, LanguageClientOptions, ServerOptions} from 'vscode-languageclient';

let client: LanguageClient;
const executablePath = '..\\..\\mypyls\\main.py';

export function activate(context: vscode.ExtensionContext) {
	let clientOptions: LanguageClientOptions = {
		documentSelector: [
			{scheme: 'file', language: 'python'}
		]
	};
	let serverOptions: ServerOptions = {
		command: 'python',
		args: [executablePath]
	};
	client = new LanguageClient('pylsp', 'pylsp', serverOptions, clientOptions);
	client.start();
}

export function deactivate(){
	if(!client){
		return undefined;
	}
	return client.stop();
}