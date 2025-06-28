using Microsoft.AspNetCore.Mvc;

//Bu kotrolcü Python API na ses kaydını, başlatma ve durdurma isteklerini gönderir.
namespace AuidoRecordingAPI.Controllers
{
    [Route("api/recording")]
    [ApiController]

    public class RecordingController : ControllerBase
    {
        private readonly HttpClient _httpClient;

        public RecordingController(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }

        //Ses kaydını başlatan çağrı
        [HttpPost("start")]
        public async Task<IActionResult> StartRecording()
        {
            var response = await _httpClient.PostAsync("http://127.0.0.1:8000/start-recording", null);
            return StatusCode((int)response.StatusCode, await response.Content.ReadAsStringAsync());
        }

        //Ses kaydını durduran çağrı
        [HttpPost("stop")]
        public async Task<IActionResult> StopRecording()
        {
            var response = await _httpClient.PostAsync("http://127.0.0.1:8000/stop-recording", null);
            return StatusCode((int)response.StatusCode, await response.Content.ReadAsStringAsync());
        }

        //Veritabanı için ses kaydını başlatır
        [HttpPost("start-database")]
        public async Task<IActionResult> StartRecordingForDatabase()
        {
            var response = await _httpClient.PostAsync("http://127.0.0.1:8000/start-recording-database", null);
            return StatusCode((int)response.StatusCode, await response.Content.ReadAsStringAsync());
        }

        //Veritabanı için ses kaydını durdurur
        [HttpPost("stop-database")]
        public async Task<IActionResult> StopRecordingForDatabase(string name)
        {
            var response = await _httpClient.PostAsync("http://127.0.0.1:8000/stop-recording-database?name="+name+"", null);
            return StatusCode((int)response.StatusCode, await response.Content.ReadAsStringAsync());
        }
    }
}