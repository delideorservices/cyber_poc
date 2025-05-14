<?php

namespace App\Http\Controllers;

use App\Models\User;
use App\Models\Skill;
use App\Models\Certification;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rule;

class UserProfileController extends Controller
{
    public function show(Request $request)
    {
        $user = $request->user();
        // dd($user);
        // Load relationships
        $user->load(['sector', 'role', 'skills', 'certifications']);
        
        return response()->json($user);
    }
    
    public function update(Request $request)
    {
        $user = $request->user();
        
        $validator = Validator::make($request->all(), [
            'name' => 'sometimes|string|max:255',
            'email' => [
                'sometimes',
                'email',
                Rule::unique('users')->ignore($user->id),
            ],
            'gender' => 'sometimes|in:male,female,other,prefer_not_to_say',
            'age' => 'sometimes|integer|min:18|max:100',
            'sector_id' => 'sometimes|exists:sectors,id',
            'role_id' => 'sometimes|exists:roles,id',
            'years_experience' => 'sometimes|integer|min:0|max:50',
            'learning_goal' => 'sometimes|string|max:255',
            'preferred_language' => 'sometimes|string|max:10',
        ]);
        
        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }
        
        // Update user profile
        $user->fill($validator->validated());
        $user->save();
        
        // Reload relationships
        $user->load(['sector', 'role', 'skills', 'certifications']);
        
        return response()->json($user);
    }
    
    public function addSkill(Request $request)
    {
        $user = $request->user();
        
        $validator = Validator::make($request->all(), [
            'skill_id' => 'required|exists:skills,id',
            'proficiency_level' => 'required|integer|min:1|max:5',
        ]);
        
        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }
        
        // Check if user already has this skill
        if ($user->skills()->where('skill_id', $request->skill_id)->exists()) {
            // Update existing skill proficiency
            $user->skills()->updateExistingPivot($request->skill_id, [
                'proficiency_level' => $request->proficiency_level
            ]);
        } else {
            // Add new skill
            $user->skills()->attach($request->skill_id, [
                'proficiency_level' => $request->proficiency_level
            ]);
        }
        
        // Reload user with relationships
        $user->load(['sector', 'role', 'skills', 'certifications']);
        
        return response()->json($user);
    }
    
    public function removeSkill(Request $request, Skill $skill)
    {
        $user = $request->user();
        
        // Detach the skill
        $user->skills()->detach($skill->id);
        
        // Reload user with relationships
        $user->load(['sector', 'role', 'skills', 'certifications']);
        
        return response()->json($user);
    }
    
    public function addCertification(Request $request)
    {
        $user = $request->user();
        
        $validator = Validator::make($request->all(), [
            'certification_id' => 'required|exists:certifications,id',
            'obtained_date' => 'nullable|date',
            'expiry_date' => 'nullable|date|after:obtained_date',
        ]);
        
        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }
        
        // Check if user already has this certification
        if ($user->certifications()->where('certification_id', $request->certification_id)->exists()) {
            // Update existing certification
            $user->certifications()->updateExistingPivot($request->certification_id, [
                'obtained_date' => $request->obtained_date,
                'expiry_date' => $request->expiry_date
            ]);
        } else {
            // Add new certification
            $user->certifications()->attach($request->certification_id, [
                'obtained_date' => $request->obtained_date,
                'expiry_date' => $request->expiry_date
            ]);
        }
        
        // Reload user with relationships
        $user->load(['sector', 'role', 'skills', 'certifications']);
        
        return response()->json($user);
    }
    
    public function removeCertification(Request $request, Certification $certification)
    {
        $user = $request->user();
        
        // Detach the certification
        $user->certifications()->detach($certification->id);
        
        // Reload user with relationships
        $user->load(['sector', 'role', 'skills', 'certifications']);
        
        return response()->json($user);
    }
    
    public function updatePassword(Request $request)
    {
        $user = $request->user();
        
        $validator = Validator::make($request->all(), [
            'current_password' => 'required',
            'new_password' => 'required|min:8',
            'new_password_confirmation' => 'required|same:new_password',
        ]);
        
        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }
        
        // Check current password
        if (!Hash::check($request->current_password, $user->password)) {
            return response()->json(['message' => 'Current password is incorrect'], 401);
        }
        
        // Update password
        $user->password = Hash::make($request->new_password);
        $user->save();
        
        return response()->json(['message' => 'Password updated successfully']);
    }
}
