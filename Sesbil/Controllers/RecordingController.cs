using System.Diagnostics;
using Microsoft.AspNetCore.Mvc;
using Sesbil.Models;
using NAudio.Wave;

namespace AuidoRecordingAPI.Controllers{
    [Route ("api/[Controller]")]
    [ApiController]

    class RecordingController : ControllerBase{
        private static WaveInEvent waveIn;
        private static bool isRecording = false;

        [HttpPost("start")]
        public IActionResult StartRecording(){
            try{
                 if(isRecording){
                return BadRequest("Kayıt zaten başlatılmış.");
            }

            waveIn = new WaveInEvent
            {
                DeviceNumber = 0,  // Varsayılan mikrofon
                WaveFormat = new WaveFormat(44100, 1)  // 44.1 kHz mono format
            };

            waveIn.DataAvailable+=(sender,e) =>
            {
                // Burdan pythona gönderilecek
                Console.WriteLine("Veri alındı: " + e.BytesRecorded + " byte.");
            };

            waveIn.StartRecording();
            isRecording=true;

            return Ok("Kayıt başladı.");
            }
            catch (Exception ex){
                return StatusCode(500, $"Kayıt başlatma hatası: {ex.Message}");
            }
        }

        [HttpPost("stop")]
        public IActionResult StopRecording(){
            try{
                if(!isRecording){
                return BadRequest("Kayıt zaten durdurulmuş.");
            }

            waveIn.StopRecording();
            isRecording = false;

            return Ok("Kayıt durduruldu.");
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Kayıt durdurma hatası: {ex.Message}");
                }        
        }
    }
} 