using Microsoft.AspNetCore.Mvc;


namespace AuidoRecordingAPI.Controllers{
    [Route ("api/[Controller]")]
    [ApiController]

    class RecordingController : ControllerBase{
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
    } 
}