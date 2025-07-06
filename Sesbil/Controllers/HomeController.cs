using Microsoft.AspNetCore.Mvc;

namespace Sesbil.Controllers;

public class HomeController : Controller
{
    public IActionResult Record()
    {
        return View();
    }
}