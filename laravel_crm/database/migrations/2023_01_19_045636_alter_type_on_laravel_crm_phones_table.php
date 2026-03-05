<?php

use Illuminate\Database\Migrations\Migration;

class AlterTypeOnLaravelCrmPhonesTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        // Skip this migration for SQLite (MySQL-specific syntax)
        if (config('database.default') !== 'mysql') {
            return;
        }

        DB::statement('ALTER TABLE '.config('laravel-crm.db_table_prefix')."phones CHANGE COLUMN type type ENUM('work','home','mobile','fax','other') NOT NULL DEFAULT 'work'");
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        DB::statement('ALTER TABLE '.config('laravel-crm.db_table_prefix')."phones CHANGE COLUMN type type ENUM('work','home','mobile','other') NOT NULL DEFAULT 'work'");
    }
}
