<?php

namespace App\Providers;

use Illuminate\Support\ServiceProvider;
use App\Services\AgentService;
class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     */
    public function register(): void
    {
        $this->app->singleton(AgentService::class, function ($app) {
            return new AgentService();
        });
    }

    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        //
    }
}
