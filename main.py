import streamlit as st
import pandas as pd
import json
from datetime import datetime

# Page config
st.set_page_config(page_title="Workout Program Designer", layout="wide")

# Initialize session state
@st.cache_data
def load_exercise_data(filepath):
    """Load exercise data from CSV with caching for improved performance."""
    try:
        df = pd.read_csv(filepath)
        df.insert(0, 'id', range(1, len(df) + 1))
        return df.to_dict('records')
    except FileNotFoundError:
        # Fallback sample data if CSV not found
        return [
            {'id': 1, 'Exercise': 'Barbell Squat', 'Body_Part': 'Squat', 'Category': 'Movement_Pattern'},
            {'id': 2, 'Exercise': 'Bench Press', 'Body_Part': 'Horizontal Push', 'Category': 'Movement_Pattern'},
            {'id': 3, 'Exercise': 'Deadlift', 'Body_Part': 'Hinge', 'Category': 'Movement_Pattern'},
            {'id': 4, 'Exercise': 'Pull Ups', 'Body_Part': 'Vertical Pull', 'Category': 'Movement_Pattern'},
        ]
    
if 'exercises' not in st.session_state:
    st.session_state.exercises = load_exercise_data('combined_exercise_library.csv')

if 'programs' not in st.session_state:
    st.session_state.programs = []

if 'current_program_idx' not in st.session_state:
    st.session_state.current_program_idx = None


# Helper functions
def get_next_id(items):
    return max([item['id'] for item in items], default=0) + 1

def add_new_exercise(ex_name, ex_cat, ex_body_part):#, ex_notes=''):
    all_exs = st.session_state.exercises
    max([ex['id'] for ex in all_exs])
    new_exercise = {'id': max([ex['id'] for ex in all_exs]) + 1,
                    'Body_Part': ex_body_part,
                    'Exercise': ex_name,
                    'Category': ex_cat}
    st.session_state.exercises.append(new_exercise)

def create_new_program(name):
    new_program = {
        'id': get_next_id(st.session_state.programs),
        'name': name,
        'weeks': [{
            'id': 1,
            'name': 'Week 1',
            'days': [{
                'id': 1,
                'name': 'Day 1',
                'exercises': []
            }]
        }]
    }
    st.session_state.programs.append(new_program)
    st.session_state.current_program_idx = len(st.session_state.programs) - 1

# add to programs, weeks, days
def add_week_to_program(program_idx):
    program = st.session_state.programs[program_idx]
    new_week = {
        'id': get_next_id(program['weeks']),
        'name': f"Week {len(program['weeks']) + 1}",
        'days': [{
            'id': 1,
            'name': 'Day 1',
            'exercises': []
        }]
    }
    st.session_state.programs[program_idx]['weeks'].append(new_week)

def add_day_to_week(program_idx, week_idx):
    week = st.session_state.programs[program_idx]['weeks'][week_idx]
    new_day = {
        'id': get_next_id(week['days']),
        'name': f"Day {len(week['days']) + 1}",
        'exercises': []
    }
    st.session_state.programs[program_idx]['weeks'][week_idx]['days'].append(new_day)

def add_exercise_to_day(program_idx, week_idx, day_idx, exercise):
    new_workout_ex = {
        'id': datetime.now().timestamp(),
        'exercise_id': exercise['id'],
        'name': exercise['Exercise'],
        'sets': 3,
        'reps': 10,
        'notes': ''
    }
    st.session_state.programs[program_idx]['weeks'][week_idx]['days'][day_idx]['exercises'].append(new_workout_ex)

# remove from programs, weeks, days
def delete_program(program_idx):
    st.session_state.programs.pop(program_idx)
    if st.session_state.current_program_idx == program_idx:
        st.session_state.current_program_idx = None
    elif st.session_state.current_program_idx and st.session_state.current_program_idx > program_idx:
        st.session_state.current_program_idx -= 1

def delete_week(program_idx, week_idx):
    st.session_state.programs[program_idx]['weeks'].pop(week_idx)

def delete_day(program_idx, week_idx, day_idx):
    st.session_state.programs[program_idx]['weeks'][week_idx]['days'].pop(day_idx)

def delete_exercise_from_day(program_idx, week_idx, day_idx, exercise_idx):
    st.session_state.programs[program_idx]['weeks'][week_idx]['days'][day_idx]['exercises'].pop(exercise_idx)

# repeat weeks or days 
def repeat_week(program_idx, week_idx):
    program = st.session_state.programs[program_idx]
    week_to_rep = program['weeks'][week_idx]
    #only adjust id and name, rest should stay the same
    new_week = week_to_rep.copy()
    new_week['id'] += 1
    new_week['name'] = f"Week {int(week_to_rep['name'][-1]) + 1}" #or f"Week {len(program['weeks']) + 2}"

    st.session_state.programs[program_idx]['weeks'].append(new_week)


# export to json or csv
def export_program_json(program):
    return json.dumps(program, indent=2)

def export_program_csv(program):
    """Export program to CSV with specific formatting"""
    csv_lines = []
    
    # Add program name as title
    csv_lines.append(f'"{program["name"]}"')
    csv_lines.append('')
    
    for week_idx, week in enumerate(program['weeks']):
        # Empty rows before week
        csv_lines.append('')
        csv_lines.append('')
        
        # Week header with empty column before
        csv_lines.append(f'"{week["name"]}"')
        
        # Find max exercises in any day this week
        max_exercises = max([len(day['exercises']) for day in week['days']], default=0)
        
        # Day headers row
        header_row = []
        for day_idx, day in enumerate(week['days']):
            header_row.append('')  # Empty column before
            header_row.append(f'"{day["name"]}"')
            for i in range(6):  # Span across remaining columns
                header_row.append('')
            if day_idx < len(week['days']) - 1:
                header_row.append('')  # Spacing between days
        csv_lines.append(','.join(header_row))
        
        # Column headers row
        col_headers = []
        for day_idx, day in enumerate(week['days']):
            col_headers.append('')  # Empty column before
            col_headers.extend(['"Exercise"', '"Sets"', '"Reps"', '"Intensity"', '"Load"', '"Actual"', '"Comments"'])
            if day_idx < len(week['days']) - 1:
                col_headers.append('')  # Spacing between days
        csv_lines.append(','.join(col_headers))
        
        # Exercise rows
        for i in range(max_exercises):
            row = []
            for day_idx, day in enumerate(week['days']):
                row.append('')  # Empty column before
                if i < len(day['exercises']):
                    ex = day['exercises'][i]
                    row.extend([
                        f'"{ex["name"]}"',
                        f'"{ex["sets"]}"',
                        f'"{ex["reps"]}"',
                        '""',  # Intensity
                        '""',  # Load
                        '""',  # Actual
                        f'"{ex.get("notes", "")}"'
                    ])
                else:
                    row.extend(['""'] * 7)  # Empty cells
                if day_idx < len(week['days']) - 1:
                    row.append('')  # Spacing between days
            csv_lines.append(','.join(row))
        
        # Empty rows after week
        csv_lines.append('')
        csv_lines.append('')
        
        # Separator line between weeks
        if week_idx < len(program['weeks']) - 1:
            separator_cells = len(week['days']) * 9
            csv_lines.append(','.join(['""'] * separator_cells))
    
    return '\n'.join(csv_lines)

# Main app
st.title("💪 Workout Program Designer")

with st.sidebar:
   st.header("📚 Exercise Library")

   with st.expander("🏋️ Create Custom Exercise", expanded = False):
        with st.form(key='custom_exercise_form'):
            all_cats = sorted(list(set([ex['Category'] for ex in st.session_state.exercises])))
            all_bps = sorted(list(set([ex['Body_Part'] for ex in st.session_state.exercises])))

            nex_name = st.text_input(label='Name', key='custom_exercise_name')
            nex_cat = st.selectbox(
                'Category',
                options=[''] + all_cats,
                format_func=lambda x: 'Select or type below...' if x == '' else x
            )
            # If nothing selected, allow custom input
            if not nex_cat:
                nex_cat = st.text_input('Or enter custom category', key = 'custom_cat')
            
            nex_bp = st.selectbox(
                'Body Part',
                options=[''] + all_bps,
                format_func=lambda x: 'Select or type below...' if x == '' else x
            )
            # If nothing selected, allow custom input
            if not nex_bp:
                nex_bp = st.text_input('Or enter custom category', key = 'custom_bp')
            #nex_bp = st.text_input(label='Body Part', key='custom_exercise_bp')
            #ex_notes = st.text_input(label = 'Notes', key = 'custom_exercise_notes')

            submitted = st.form_submit_button("Click Here to Add Exercise")

            if submitted:
                if nex_name and nex_cat and nex_bp:
                    # Add your logic here to save the exercise to your library
                    st.success(f"Added {nex_name} to exercise library!")
                    add_new_exercise(nex_name, nex_cat, nex_bp)
                    st.rerun()
                else:
                    st.error("Please fill in all fields")

    
   # Search and filter
   search_term = st.text_input("🔍 Search exercises", "")
       
   categories = ['All'] + sorted(list(set([ex['Category'] for ex in st.session_state.exercises])))
   filter_category = st.selectbox("Filter by category", categories)
       
   body_parts = ['All'] + sorted(list(set([ex['Body_Part'] for ex in st.session_state.exercises])))
   filter_body_part = st.selectbox("Filter by body part", body_parts)
       
   # Display exercises
   st.subheader("Available Exercises")
       
   exercises_df = pd.DataFrame(st.session_state.exercises)
       
   # Apply filters
   if search_term:
       exercises_df = exercises_df[exercises_df['Exercise'].str.contains(search_term, case=False)]
   if filter_category != 'All':
       exercises_df = exercises_df[exercises_df['Category'] == filter_category]
   if filter_body_part != 'All':
       exercises_df = exercises_df[exercises_df['Body_Part'] == filter_body_part]
       
   # Display exercises
   for idx, exercise in exercises_df.iterrows():
       with st.container():#,height=100):
           st.markdown(f"**{exercise['Exercise']}**")
           st.caption(f"{exercise['Body_Part']} • {exercise['Category']}")
           st.divider() 

#program functionality
st.header("📋 My Programs")

# Create new program
col_new1, col_new2 = st.columns([3, 1])
with col_new1:
    new_program_name = st.text_input("New program name", "")
with col_new2:
    st.write("")  # Spacing
    if st.button("Create Program"):
        if new_program_name:
            create_new_program(new_program_name)
            st.rerun()

st.divider()

# Display programs
if len(st.session_state.programs) == 0:
    st.info("No programs yet. Create one to get started!")
else:
    # Program selector
    program_names = [p['name'] for p in st.session_state.programs]
    
    if st.session_state.current_program_idx is not None:
        default_idx = st.session_state.current_program_idx
    else:
        default_idx = 0
    
    selected_program_name = st.selectbox(
        "Select a program to edit",
        program_names,
        index=default_idx
    )
    st.session_state.current_program_idx = program_names.index(selected_program_name)
    
    current_program = st.session_state.programs[st.session_state.current_program_idx]
    
    # Program actions
    col_act1, col_act2, col_act3, col_act4 = st.columns(4)
    with col_act1:
        if st.button("🗑️ Delete Program"):
            delete_program(st.session_state.current_program_idx)
            st.rerun()
    with col_act2:
        st.download_button(
            label="📥 CSV",
            data=export_program_csv(current_program),
            file_name=f"{current_program['name'].replace(' ', '_')}.csv",
            mime="text/csv"
        )
    with col_act3:
        st.download_button(
            label="📥 JSON",
            data=export_program_json(current_program),
            file_name=f"{current_program['name'].replace(' ', '_')}.json",
            mime="application/json"
        )
    with col_act4:
        if st.button("➕ Add Week"):
            add_week_to_program(st.session_state.current_program_idx)
            st.rerun()
    
    st.divider()
    
    # Display weeks
    for week_idx, week in enumerate(current_program['weeks']):
        with st.expander(f"📅 {week['name']}", expanded=True):
            # Week name editor
            new_week_name = st.text_input(
                "Week name",
                value=week['name'],
                key=f"week_name_{st.session_state.current_program_idx}_{week_idx}"
            )
            if new_week_name != week['name']:
                st.session_state.programs[st.session_state.current_program_idx]['weeks'][week_idx]['name'] = new_week_name
            
            # Week actions
            col_w1, col_w2, col_w3 = st.columns([1, 1, 1])
            with col_w1:
                if st.button("➕ Add Day", key=f"add_day_{week_idx}"):
                    add_day_to_week(st.session_state.current_program_idx, week_idx)
                    st.rerun()
            with col_w2:
                if st.button("🗑️ Delete Week", key=f"del_week_{week_idx}"):
                    delete_week(st.session_state.current_program_idx, week_idx)
                    st.rerun()
            
            with col_w3:
                if st.button("➕ Repeat Week", key=f"rep_week_{week_idx}"):
                    repeat_week(st.session_state.current_program_idx, week_idx)
                    st.rerun()
            
            st.divider()
            
            # Display days - each day in its own section
            for day_idx, day in enumerate(week['days']):
                with st.expander(f"### 📆 {day['name']}", expanded=True):
                
                # Day controls
                    col_d1, col_d2 = st.columns([3, 1])
                    with col_d1:
                        new_day_name = st.text_input(
                            "Rename day",
                            value=day['name'],
                            key=f"day_name_{week_idx}_{day_idx}",
                            label_visibility="collapsed"
                        )
                        if new_day_name != day['name']:
                            st.session_state.programs[st.session_state.current_program_idx]['weeks'][week_idx]['days'][day_idx]['name'] = new_day_name

                    with col_d2:
                        if st.button("🗑️ Delete Day", key=f"del_day_{week_idx}_{day_idx}"):
                            delete_day(st.session_state.current_program_idx, week_idx, day_idx)
                            st.rerun()
                
                    # Display exercises
                    if len(day['exercises']) == 0:
                        st.info("No exercises yet. Select one below to add.")
                    else:
                        for ex_idx, exercise in enumerate(day['exercises']):
                            with st.container():
                                st.markdown(f"**{exercise['name']}**")
                                
                                col_ex1, col_ex2, col_ex3 = st.columns([1, 1, 1])
                                
                                with col_ex1:
                                    new_sets = st.number_input(
                                        "Sets",
                                        min_value=1,
                                        value=exercise['sets'],
                                        key=f"sets_{week_idx}_{day_idx}_{ex_idx}"
                                    )
                                    if new_sets != exercise['sets']:
                                        st.session_state.programs[st.session_state.current_program_idx]['weeks'][week_idx]['days'][day_idx]['exercises'][ex_idx]['sets'] = new_sets
                                
                                with col_ex2:
                                    new_reps = st.number_input(
                                        "Reps",
                                        min_value=1,
                                        value=exercise['reps'],
                                        key=f"reps_{week_idx}_{day_idx}_{ex_idx}"
                                    )
                                    if new_reps != exercise['reps']:
                                        st.session_state.programs[st.session_state.current_program_idx]['weeks'][week_idx]['days'][day_idx]['exercises'][ex_idx]['reps'] = new_reps
                                
                                with col_ex3:
                                    if st.button("🗑️", key=f"del_ex_{week_idx}_{day_idx}_{ex_idx}"):
                                        delete_exercise_from_day(st.session_state.current_program_idx, week_idx, day_idx, ex_idx)
                                        st.rerun()
                                
                                new_notes = st.text_input(
                                    "Notes",
                                    value=exercise.get('notes', ''),
                                    key=f"notes_{week_idx}_{day_idx}_{ex_idx}"
                                )
                                if new_notes != exercise.get('notes', ''):
                                    st.session_state.programs[st.session_state.current_program_idx]['weeks'][week_idx]['days'][day_idx]['exercises'][ex_idx]['notes'] = new_notes
                                
                                st.divider()
                    
                    # Add exercise section
                    st.markdown("**⬇️ Add Exercise**")
                    
                    # Create exercise options
                    exercise_options = ["Select an exercise..."] + [f"{ex['Exercise']} ({ex['Body_Part']})" for ex in exercises_df.to_dict('records')]
                    exercise_mapping = {f"{ex['Exercise']} ({ex['Body_Part']})": ex for ex in exercises_df.to_dict('records')}
                    
                    selected_exercise_str = st.selectbox(
                        "Choose exercise",
                        options=exercise_options,
                        key=f"add_ex_select_{week_idx}_{day_idx}",
                        label_visibility="collapsed"
                    )
                    
                    if st.button("Add to Day", key=f"add_ex_btn_{week_idx}_{day_idx}"):
                        if selected_exercise_str != "Select an exercise...":
                            exercise = exercise_mapping.get(selected_exercise_str)
                            if exercise:
                                add_exercise_to_day(st.session_state.current_program_idx, week_idx, day_idx, exercise)
                                st.rerun()
                        else:
                            st.warning("Please select an exercise first!")
                    
                    st.markdown("---")

# Footer
st.markdown("---")
st.caption("💡 Tip: All data is stored in your browser session. Export your programs as CSV or JSON files to save them permanently.")