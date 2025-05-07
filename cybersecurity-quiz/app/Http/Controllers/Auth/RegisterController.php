<?php

namespace App\Http\Controllers\Auth;

use App\Http\Controllers\Controller;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Validator;

class RegisterController extends Controller
{
    public function register(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'name' => 'required|string|max:255',
            'email' => 'required|string|email|max:255|unique:users',
            'password' => 'required|string|min:8|confirmed',
            'gender' => 'nullable|in:male,female,other,prefer_not_to_say',
            'age' => 'nullable|integer|min:18|max:100',
            'sector_id' => 'nullable|exists:sectors,id',
            'role_id' => 'nullable|exists:roles,id',
            'years_experience' => 'nullable|integer|min:0|max:50',
            'learning_goal' => 'nullable|string|max:255',
        ]);

        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }

        $user = User::create([
            'name' => $request->name,
            'email' => $request->email,
            'password' => Hash::make($request->password),
            'gender' => $request->gender,
            'age' => $request->age,
            'sector_id' => $request->sector_id,
            'role_id' => $request->role_id,
            'years_experience' => $request->years_experience,
            'learning_goal' => $request->learning_goal,
            'preferred_language' => $request->preferred_language ?? 'en',
        ]);

        // Process skills and certifications if provided
        if ($request->has('skills')) {
            foreach ($request->skills as $skill) {
                $user->skills()->attach($skill['id'], [
                    'proficiency_level' => $skill['proficiency_level'] ?? 1
                ]);
            }
        }

        if ($request->has('certifications')) {
            foreach ($request->certifications as $cert) {
                $user->certifications()->attach($cert['id'], [
                    'obtained_date' => $cert['obtained_date'] ?? null,
                    'expiry_date' => $cert['expiry_date'] ?? null
                ]);
            }
        }

        $token = $user->createToken('auth-token')->plainTextToken;

        return response()->json([
            'user' => $user,
            'token' => $token
        ]);
    }
}
