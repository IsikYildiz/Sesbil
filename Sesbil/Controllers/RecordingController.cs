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
            return StatusCode((int)response.StatusCode, await response.Content.ReadAsStringAsync());
        }

        [HttpGet("information")]
        public async Task<IActionResult> GetInformation()
        {
            var response = await _httpClient.GetAsync("http://127.0.0.1:8000/get-information");
            if (response.IsSuccessStatusCode)
            {
                var data = await response.Content.ReadAsStringAsync();
                return Ok(data);
            }
            return StatusCode((int)response.StatusCode, await response.Content.ReadAsStringAsync());
        }
    } 
}