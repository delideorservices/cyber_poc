<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\HomeController;

// Redirect all routes to SPA entry point
Route::get('/{any?}', function () {
    return view('app');
})->where('any', '^(?!api).*$');