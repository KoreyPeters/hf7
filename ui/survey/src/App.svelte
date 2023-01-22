<script>
    export let survey_data;

    console.log(survey_data)

    function updateSurveyData(){
        console.log("Updated")
        document.getElementById('survey-results').setAttribute('value', JSON.stringify(survey_data))
    }

</script>

<main>
    <p>Please select all that are true.</p>
    <table>
        {#each survey_data as criterion}
            <tr>
                <input bind:checked={criterion.response} type="checkbox" on:change={updateSurveyData}>
                <span class:checked={criterion.response}>{criterion.question}</span>
                <br/>
            </tr>
        {/each}
    </table>
</main>