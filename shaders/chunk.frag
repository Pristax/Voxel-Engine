#version 330 core

layout (location = 0) out vec4 fragColor;

const vec3 gamma = vec3(2.2);
const vec3 inv_gamma = 1.0 / gamma;

// Zvedni/sniž podle chuti:
const float AMBIENT_LIGHT = 0.55;
const float DIRECT_LIGHT = 0.75;
const float EXPOSURE = 1.0;
const float FOG_DENSITY = 0.00000065;

uniform sampler2DArray u_texture_array_0;
uniform vec3 bg_color;
uniform float water_line;

in vec2 uv;
in float shading;
in vec3 frag_world_pos;

flat in int face_id;
flat in int voxel_id;


void main() {
    vec2 face_uv = uv;
    face_uv.x = uv.x / 3.0 - min(face_id, 2) / 3.0;

    vec3 tex_col = texture(u_texture_array_0, vec3(face_uv, voxel_id)).rgb;

    tex_col = pow(tex_col, gamma);

    // tex_col *= shading;
    float light = AMBIENT_LIGHT + shading * DIRECT_LIGHT;
    tex_col *= min(light, 1.25);

    tex_col *= EXPOSURE;

    // underwater effect - méně brutální ztmavení než původní vec3(0.0, 0.3, 1.0)
    if (frag_world_pos.y < water_line) {
        tex_col *= vec3(0.35, 0.55, 1.0);
    }

    // fog
    float fog_dist = gl_FragCoord.z / gl_FragCoord.w;
    float fog_amount = 1.0 - exp2(-FOG_DENSITY * fog_dist * fog_dist);
    fog_amount = clamp(fog_amount, 0.0, 1.0);
    tex_col = mix(tex_col, bg_color, fog_amount);

    tex_col = pow(tex_col, inv_gamma);
    fragColor = vec4(tex_col, 1.0);
}
