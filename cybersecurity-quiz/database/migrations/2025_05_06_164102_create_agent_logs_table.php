<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateAgentLogsTable extends Migration
{
    public function up()
    {
        Schema::create('agent_logs', function (Blueprint $table) {
            $table->id();
            $table->string('agent_name');
            $table->string('action');
            $table->json('input')->nullable();
            $table->json('output')->nullable();
            $table->string('status'); // success, error, warning
            $table->text('error_message')->nullable();
            $table->timestamp('executed_at');
            $table->timestamps();
        });
    }

    public function down()
    {
        Schema::dropIfExists('agent_logs');
    }
}