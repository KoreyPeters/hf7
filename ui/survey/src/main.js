import App from './App.svelte';

const survey_data = JSON.parse(document.getElementById("survey-data").innerText)


const app = new App({
	target: document.getElementById('survey-widget'),
	props: {
		survey_data: survey_data,
	}
});

export default app;