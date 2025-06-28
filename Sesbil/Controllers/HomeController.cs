using Microsoft.AspNetCore.Mvc;

namespace Sesbil.Controllers;

public class HomeController : Controller
{
    public IActionResult Record()
    {
        return View();
    }
    
    public IActionResult RecordDatabase()
    {
        return View("RecordDatabase");
    }
}