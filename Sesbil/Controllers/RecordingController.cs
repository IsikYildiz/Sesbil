using Microsoft.AspNetCore.Mvc;


namespace AuidoRecordingAPI.Controllers{
    [Route ("api/recording")]
    [ApiController]

    public class RecordingController : ControllerBase{
        private readonly HttpClient _httpClient;

        public RecordingController(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }

        [HttpPost("start")]
        public async Task<IActionResult> StartRecording()
        {
            var response = await _httpClient.PostAsync("http://127.0.0.1:8000/start-recording", null);
            return StatusCode((int)response.StatusCode, await response.Content.ReadAsStringAsync());
        }

        [HttpPost("stop")]
        public async Task<IActionResult> StopRecording()
        {
            var response = await _httpClient.PostAsync("http://127.0.0.1:8000/stop-recording", null);
            if (response.IsSuccessStatusCode)
            {
                var speechToText = await response.Content.ReadAsStringAsync();
                return Ok(speechToText);
            }
            return StatusCode((int)response.StatusCode, await response.Content.ReadAsStringAsync());
        }

        [HttpPost("finish")]
        public async Task<IActionResult> FinishRecording()
        {
            var response = await _httpClient.PostAsync("http://127.0.0.1:8000/finish-recording", null);
            return StatusCode((int)response.StatusCode, await response.Content.ReadAsStringAsync());
        }

        [HttpGet("histogram")]
        public async Task<IActionResult> GetHistogram()
        {
            var response = await _httpClient.GetAsync("http://127.0.0.1:8000/get-histogram");
            if (response.IsSuccessStatusCode)
            {
                var histogram = await response.Content.ReadAsStringAsync();
                return Ok(histogram);
            }
            return StatusCode((int)response.StatusCode, await response.Content.ReadAsStringAsync());
        }

        [HttpGet("information")]
        public async Task<IActionResult> GetInformation()
        {
            var response = await _httpClient.GetAsync("http://127.0.0.1:8000/get-information");
            if (response.IsSuccessStatusCode)
            {
                var speechText = await response.Content.ReadAsStringAsync();
                return Ok(speechText);
            }
            return StatusCode((int)response.StatusCode, await response.Content.ReadAsStringAsync());
        }
    } 
}