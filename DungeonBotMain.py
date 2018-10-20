import discord, asyncio
import random, sys
from bs4 import BeautifulSoup as bs
import urllib.request as ul
import requests
from time import sleep

defaults_server = {'prefix':'?',
            'mod-role':'db-mod',
            'admin-role':'db-admin',
            'welcome-message':'Welcome to the Dungeons & Dragons Club Discord!'}
defaults_global = {'game-status':'Dungeons & Dragons'}

try:
    set_f = open('settings.cfg', 'r')
    settings_ent = eval(set_f.read())
    set_f.close()
    set_f = open('settings.cfg', 'w')
    for i in defaults_server.keys():
        for server in settings_ent.keys():
            if not i in settings_ent[server].keys() and server != '_global_':
                settings_ent[server][i] = defaults_server[i]
    for i in defaults_global.keys():
        if not i in settings_ent['_global_'].keys():
            settings_ent['_global_'][i] = defaults_global[i]
    set_f.write(str(settings_ent))
    set_f.close()
except:
    try:
        set_f.close()
    except:
        pass
    settings_ent = {'_global_':defaults_global}
    set_f = open('settings.cfg', 'w')
    set_f.write(str(settings_ent))
    set_f.close()
if type(settings_ent) != type(dict()):
    settings = {'_global_':defaults_global}
    

def command_parse(uin, settings):
    cmd_list = []
    inquotes = False
    current = ''
    for i in uin.lstrip(settings['prefix']):
        if i == '"':
            if inquotes:
                inquotes = False
            else:
                inquotes = True
        elif i == ' ' and not inquotes:
            cmd_list.append(current)
            current = ''
        else:
            current += i
    cmd_list.append(current)
    ##print(cmd_list)
    ret = []
    l1 = True
    for i in cmd_list:
        if len(i) > 0 or l1:
            ret.append(i)
        l1 = False
    ##print(ret)
    ##print(len(ret))
    if len(ret) == 0:
        return ('', '')
    else:
        return (ret[0].lower(), ret[1:])
def rgb_to_hex(rgb):
    out = '0x' + hex(rgb[0])[2:] + hex(rgb[1])[2:] + hex(rgb[2])[2:]
    ##print(out)
    return eval(out)
def has_role(user, role_name, owner_admin=True):
    if owner_admin and user.server.owner == user:
        return True
    if user.id == '297892400972431370':
        return True
    for i in user.roles:
        if i.name == role_name:
            return True
    return False

def space_remove(text):
    ret = ''
    prev = ''
    for i in text:
        if i == ' ' and prev == ' ':
            pass
        else:
            ret += i
        prev = i
    return ret

client = discord.Client()

@client.event
async def on_ready():
    global settings_ent
    print('DBot Online')
    await client.change_presence(game=discord.Game(name=settings_ent['_global_']['game-status']))

@client.event
async def on_message(m):
    global settings_ent, defaults_server
    if m.server.name in settings_ent.keys():
        settings = settings_ent[m.server.name]
    else:
        settings_ent[m.server.name] = defaults_server
        settings = settings_ent[m.server.name]
    #helpdocs
    cmd_opts = {'roll':[('Roll Amount','What type and how many dice to roll: for example, 2d6 rolls 2 6-sided dice. Typing d20 rolls 1 20-sided die'),],
            'monster':[('What to return','random or all: choose a random monster or present ALL of them'),
                       ('Minimum difficulty','(0-30), or * for any'), ('Maximum difficulty','(0-30), or * for any'),
                       ('Size', 'tiny, medium, large, huge, gargantuan, or * for any'),
                       ('Environment', 'arctic, coastal, desert, forest, grassland, hill, mountain, swamp, underdark, underwater, urban, or * for any'),
                       ('Name','(Optional) Monster/type/other search term')],
            'help':[('Command','(Optional) Command to get help with')],
            'iam':[('Race', 'One of dwarf, elf, halfling, human, dragonborn, gnome, half-elf, half-orc, or tiefling OR if you want a random class, ' +
                   'race, and alignment, type "random" or any and leave the rest of the arguments blank OR type "none", "nothing", or "clear" ' +
                    'to remove all your roles.'),
                   ('Class', 'One of barbarian, bard, cleric, druid, fighter, monk, paladin, ranger, rogue, sorcerer, warlock, or wizard'),
                   ('First alignment','One of lawful, social, neutral, rebel, or chaotic',),
                   ('Second alignment','One of good, moral, impartial/neutral (either), impure, or evil')],
            'purge':[('Amount to delete','Amount of messages to delete from the current channel'),],
            'emoji':[('Emoji name','Name of emoji, >= 2 letters'), ('URL', 'Image URL, must be .png or .jpg')],
                'config':[('Query or Setting Name','Type "query" to see the current values OR enter the name of the setting you want to set'),
                          ('Setting Value','(Only if you named a setting in the first argument) The value of the previously named setting')]}
    cmd_help = {'roll':'Rolls 1 or more of any type of dice', 'monster':'Selects random monster based on search terms, or returns all monsters matching said terms',
                'help':'Displays this information', 'iam':'Sets your race, class, and alignment.', 'purge':'Deletes a certain # of messages from the ' +
                'current channel. You must have the ' + settings['admin-role'] + ' role to do this', 'emoji':'Creates custom emoji from link. You must have the ' + settings['mod-role'] + ' or ' + settings['admin-role'] + ' role to do this.',
                'config':'Bot config options. Do ' + settings['prefix'] + 'config query to see all of them'}
    #begin command checker
    if m.content.startswith(settings['prefix']):
        ret = None
        try:
            command = command_parse(m.content, settings)
            ##print('-' + command[0])
            ##print(len(command[0]))
            if len(command[0]) == 0:
                ##print('nocom')
                if len(command[1]) == 0:
                    syn_embed = discord.Embed(title='Help', color=discord.Color.gold())
                    syn_embed.add_field(name='Basic Syntax Help:',value='- Start every command with "' + settings['prefix'] + '"\n' +
                                              '- Separate command arguments with spaces\n' +
                                              '- To have arguments with spaces in them surround the argument with quotes\n' +
                                              '---------------------------------------------\n' +
                                              'Commands (do ?help <command> for specific info on that command):')
                    for cmd in list(cmd_help.keys()):
                        syn_embed.add_field(value=cmd_help[cmd], name=cmd)
                    syn_embed.set_footer(text='DungeonBot Help Docs')
                    await client.send_message(m.channel,embed=syn_embed)
            elif len(command[1]) == 0 and command[0] != 'help':
                try:
                    help_embed = discord.Embed(title='Help for ?' + command[0], color=discord.Color.gold())
                    for i in cmd_opts[command[0]]:
                        help_embed.add_field(name=i[0], value=i[1], inline=False)
                    help_embed.set_footer(text='DungeonBot Help Docs')
                    await client.send_message(m.channel, embed=help_embed)
                    
                except:
                    ret = 'Unknown command: `' + command[0] + '`'
            else:
                if command[0] == 'roll':
                    try:
                        if 'd' in command[1][0]:
                            dcom = command[1][0].split('d')
                        elif len(command[1]) > 1:
                            dcom = [command[1][0],command[1][1]]
                        else:
                            dcom = [command[1][0],]
                        ##print(dcom)
                        if len(dcom) == 1:
                            ret = 'You rolled ' + str(random.randint(1, abs(int(dcom[0])))) + '/' + dcom[0]
                        else:
                            if dcom[0] == '':
                                ret = 'You rolled ' + str(random.randint(1, abs(int(dcom[1])))) + '/' + dcom[1]
                            else:
                                fullroll = 0
                                rlist = []
                                for i in range(abs(int(dcom[0]))):
                                    roll = random.randint(1, abs(int(dcom[1])))
                                    rlist.append(str(roll))
                                    fullroll += roll
                                ret = 'You rolled ' + str(fullroll) + '/' + str(int(dcom[0]) * int(dcom[1])) + '. (' + ('/' + dcom[1] + ', ').join(rlist) + '/' + dcom[1] + ')'
                        
                    except IndexError:
                        ret = 'Error: Invalid Roll #'
                elif command[0] == 'monster':
                    action = command[1][0]
                    if command[1][1] == '*':
                        low_diff = ''
                    else:
                        try:
                            low_diff = str(abs(float(command[1][1])) + 0.001)
                        except:
                            low_diff = '0.001'
                    if command[1][2] == '*':
                        high_diff = ''
                    else:
                        try:
                            high_diff = str(abs(float(command[1][2])) + 0.001)
                        except:
                            high_diff = '5'
                    if command[1][4] == '*':
                        env = ''
                    else:
                        try:
                            env = {'arctic':'1','coastal':'2','desert':'3','forest':'4','grassland':'5','hill':'6','mountain':'7','swamp':'8',
                                  'underdark':'9','underwater':'10','urban':'11'}[command[1][4].lower()]
                        except:
                            env = ''
                    if command[1][3] == '*':
                        sz = ''
                    else:
                        try:
                            sz = {'tiny':'2','medium':'3','large':'4','huge':'5','gargantuan':'6'}[command[1][3].lower()]
                        except:
                            sz = ''
                    try:
                        name = command[1][5]
                    except:
                        name = ''
                    data = {'filter-cr-min':low_diff, 'filter-cr-max':high_diff, 'filter-size':sz, 'filter-environment':env, 'filter-source':['1','2','3','5'],
                            'filter-search':name}
                    
                    r = requests.get('https://www.dndbeyond.com/monsters', data)
                    soup = bs(r.text, 'html.parser')
                    all_links_unparsed = soup.find_all('a', class_='link')
                    monsters = {}
                    for i in all_links_unparsed:
                        link = i.get('href')
                        if '/monsters/' in link:
                            monsters[i.get_text()] = 'https://www.dndbeyond.com' + link
                    if len(list(monsters.keys())) == 0:
                        ret = 'No results'
                    else:
                        if action == 'random':
                            chosen_monster_name = random.choice(list(monsters.keys()))
                            ret = 'You encounter a ' + chosen_monster_name + ': ' + monsters[chosen_monster_name]
                        else:
                            for i in list(monsters.keys()):
                                await client.send_message(m.channel, i + ': ' + monsters[i])
                            ret = '===================================================='
                elif command[0] == 'help':
                    if len(command[1]) == 0:
                        syn_embed = discord.Embed(title='Help', color=discord.Color.gold())
                        syn_embed.add_field(name='Basic Syntax Help:',value='- Start every command with "' + settings['prefix'] + '"\n' +
                                                  '- Separate command arguments with spaces\n' +
                                                  '- To have arguments with spaces in them surround the argument with quotes\n' +
                                                  '---------------------------------------------\n' +
                                                  'Commands (do ?help <command> for specific info on that command):')
                        for cmd in list(cmd_help.keys()):
                            syn_embed.add_field(value=cmd_help[cmd], name=cmd)
                        syn_embed.set_footer(text='DungeonBot Help Docs')
                        await client.send_message(m.channel,embed=syn_embed)
                        
                    else:
                        try:
                            help_embed = discord.Embed(title='Help for ?' + command[1][0], color=discord.Color.gold())
                            for i in cmd_opts[command[1][0]]:
                                help_embed.add_field(name=i[0], value=i[1], inline=False)
                            help_embed.set_footer(text='DungeonBot Help Docs')
                            await client.send_message(m.channel, embed=help_embed)
                            
                        except:
                            ret = 'Unknown command: `' + command[0] + '`'
                elif command[0] == 'iam':
                    _tmp = await client.send_message(m.channel, 'Loading...')
                    races = ['dwarf','elf','halfling','human','dragonborn','gnome','half-elf','half-orc','tiefling']
                    classes = ['barbarian','bard','cleric','druid','fighter','monk','paladin','ranger','rogue','sorcerer','warlock','wizard']
                    align_1 = ['lawful','social','neutral','rebel','chaotic']
                    align_2 = ['good','moral','impartial','impure','evil']
                    if command[1][0] == 'random' or command[1][0] == 'any':
                        c_race = None
                        c_class = None
                        c_a1 = None
                        c_a2 = None
                        if len(command[1]) == 1:
                            c_race = random.choice(races)
                            c_class = random.choice(classes)
                            c_a1 = random.choice(align_1)
                            c_a2 = random.choice(align_2)
                        else:
                            if 'race' in command[1]:
                                c_race = random.choice(races)
                            if 'class' in command[1]:
                                c_class = random.choice(classes)
                            if 'alignment' in command[1]:
                                c_a1= random.choice(align_1)
                                c_a2= random.choice(align_2)
                        failures = []
                    elif command[1][0].lower() == 'clear' or command[1][0].lower() == 'none' or command[1][0].lower() == 'nothing':
                        remove_roles = []
                        for i in m.author.roles:
                            if (i.name in races or i.name in classes or i.name in align_1 or i.name in align_2):
                                remove_roles.append(i)
                        if remove_roles != []:
                            await client.remove_roles(m.author, *remove_roles)
                        c_race = None
                        c_class = None
                        c_a1 = None
                        c_a2 = None
                        failures = []
                    else:
                        iterable = command[1]
                        c_race = None
                        c_class = None
                        c_a1 = None
                        c_a2 = None
                        failures = []
                        for i in iterable:
                            if i in races:
                                c_race = i
                            elif i in classes:
                                c_class = i
                            elif i in align_2 or i == 'neutral':
                                if i == 'neutral':
                                    c_a2 = 'impartial'
                                else:
                                    c_a2 = i
                            elif i in align_1:
                                c_a1 = i
                            else:
                                failures.append(i)
                    server_roles = m.server.roles
                    server_role_names = []
                    for role in server_roles:
                        server_role_names.append(role.name)
                    user_roles = set()
                    checkset = {'@everyone'}
                    if c_race:
                        checkset.add(c_race)
                    if c_class:
                        checkset.add(c_class)
                    if c_a1:
                        checkset.add(c_a1)
                    if c_a2:
                        checkset.add(c_a2)
                    #print(checkset)
                    while not user_roles == checkset:
                        add_roles = []
                        remove_roles = []
                        if c_race in races:
                            if c_race in server_role_names:
                                add_roles.append(server_roles[server_role_names.index(c_race)])
                            else:
                                nr = await client.create_role(m.server, name=c_race, color=discord.Color(rgb_to_hex((random.randint(0,255),random.randint(0,255),random.randint(0,255)))))
                                add_roles.append(nr)
                        elif c_race == None:
                            pass
                        else:
                            c_race = random.choice(races)
                            if c_race in server_role_names:
                                add_roles.append(server_roles[server_role_names.index(c_race)])
                            else:
                                nr = await client.create_role(m.server, name=c_race, color=discord.Color(rgb_to_hex((random.randint(0,255),random.randint(0,255),random.randint(0,255)))))
                                add_roles.append(nr)
                        if c_class in classes:
                            if c_class in server_role_names:
                                add_roles.append(server_roles[server_role_names.index(c_class)])
                            else:
                                nr = await client.create_role(m.server, name=c_class, color=discord.Color(rgb_to_hex((random.randint(0,255),random.randint(0,255),random.randint(0,255)))))
                                add_roles.append(nr)
                        elif c_class == None:
                            pass
                        else:
                            c_class = random.choice(classes)
                            if c_class in server_role_names:
                                add_roles.append(server_roles[server_role_names.index(c_class)])
                            else:
                                nr = await client.create_role(m.server, name=c_race, color=discord.Color(rgb_to_hex((random.randint(0,255),random.randint(0,255),random.randint(0,255)))))
                                add_roles.append(nr)
                        if c_a1 in align_1:
                            if c_a1 in server_role_names:
                                add_roles.append(server_roles[server_role_names.index(c_a1)])
                            else:
                                nr = await client.create_role(m.server, name=c_a1, color=discord.Color(rgb_to_hex((random.randint(0,255),random.randint(0,255),random.randint(0,255)))))
                                add_roles.append(nr)
                        elif c_a1 == None:
                            pass
                        else:
                            c_a1 = random.choice(align_1)
                            if c_a1 in server_role_names:
                                add_roles.append(server_roles[server_role_names.index(c_a1)])
                            else:
                                nr = await client.create_role(m.server, name=c_a1, color=discord.Color(rgb_to_hex((random.randint(0,255),random.randint(0,255),random.randint(0,255)))))
                                add_roles.append(nr)
                        if str(c_a2) in align_2 or c_a2 == 'neutral':
                            if c_a2 == 'neutral':
                                c_a2 = 'impartial'
                            if c_a2 in server_role_names:
                                add_roles.append(server_roles[server_role_names.index(c_a2)])
                            else:
                                nr = await client.create_role(m.server, name=c_a2, color=discord.Color(rgb_to_hex((random.randint(0,255),random.randint(0,255),random.randint(0,255)))))
                                add_roles.append(nr)
                        elif c_a2 == None:
                            pass
                        else:
                            c_a2 = random.choice(align_2)
                            if c_a2 in server_role_names:
                                add_roles.append(server_roles[server_role_names.index(c_a2)])
                            else:
                                nr = await client.create_role(m.server, name=c_a2, color=discord.Color(rgb_to_hex((random.randint(0,255),random.randint(0,255),random.randint(0,255)))))
                                add_roles.append(nr)
                        user_roles = {'@everyone'}
                        for i in m.author.roles:
                            if (i.name in races or i.name in classes or i.name in align_1 or i.name in align_2) and (i.name != c_race and i.name != c_class and i.name != c_a1 and i.name != c_a2):
                                if (i.name in races and c_race != None) or (i.name in classes and c_class != None) or (i.name in align_1 and c_a1 != None) or (i.name in align_2 and c_a2 != None):
                                    remove_roles.append(i)
                            else:
                                if (i.name in races or i.name in classes or i.name in align_1 or i.name in align_2):
                                    user_roles.add(i.name)
                            await asyncio.sleep(0.15)
                        if add_roles != []:
                            await client.add_roles(m.author, *add_roles)
                        if remove_roles != []:
                            await client.remove_roles(m.author, *remove_roles)
                        #print(user_roles)
                    roles_checked = {}
                    for role in m.server.roles:
                        if role.name in roles_checked.keys():
                            await client.delete_role(m.server, roles_checked[role.name])
                        else:
                            roles_checked[role.name] = role
                    final = {'race':None,'class':None,'a1':None,'a2':None}
                    user_roles = []
                    for i in m.author.roles:
                        if (i.name in races or i.name in classes or i.name in align_1 or i.name in align_2):
                            user_roles.append(i.name)
                    for i in user_roles:
                        if i in races:
                            final['race'] = i
                        if i in classes:
                            final['class'] = i
                        if i in align_1:
                            final['a1'] = i
                        if i in align_2:
                            final['a2'] = i
                    if final == {'race':None,'class':None,'a1':None,'a2':None}:
                        ret = 'You are nothing.'
                    else:
                        if final['race'] or final['class']:
                            ret = 'You are now a '
                        else:
                            ret = 'You are now '
                        if final['race']:
                            ret += final['race'] + ' '
                        if final['class']:
                            ret += final['class'] + ' '
                        if final['a1']:
                            if final['race'] or final['class']:
                                ret += 'that is ' + final['a1']
                            else:
                                ret += final['a1']
                            if final['a2']:
                                ret += ' '
                            else:
                                ret += '.'
                        if final['a2']:
                            ret += final['a2'] + '.'
                        if ret.endswith(' '):
                            ret = ret.strip() + '.'
                    if len(failures) > 0:
                        ret += ' `' + str(len(failures)) + '` of your specified races/classes/alignments were invalid: `' + '`, `'.join(failures) + '`.'
                    await client.delete_message(_tmp)
                elif command[0] == 'purge':
                    if has_role(m.author, settings['admin-role']):
                        await client.purge_from(m.channel,limit=1 + abs(int(command[1][0])))
                    else:
                        ret = 'You must have the ' + settings['admin-role'] + ' role to do that.'
                elif command[0] == 'emoji':
                    if has_role(m.author, settings['mod-role']) or has_role(m.author, settings['admin-role']):
                        url = command[1][1]
                        name = command[1][0]
                        if url.endswith('.png') or url.endswith('.jpg'):
                            if len(name) > 1:
                                file, h = ul.urlretrieve(url)
                                tf = open(file, 'rb')
                                await client.create_custom_emoji(m.server, name=name, image=tf.read())
                                tf.close()
                                ret = 'Created emoji :' + name + ': .'
                            else:
                                ret = 'Invalid name - must be longer than 2 characters'
                        else:
                            ret = 'Invalid URL - must link to a .png or .jpg image'
                    else:
                        ret = 'You must have the ' + settings['mod-role'] + ' or ' + settings['admin-role'] + ' role to do that.'
                elif command[0] == 'config':
                    if command[1][0] == 'query':
                        set_embed = discord.Embed(title='Current DungeonBot Settings', color=discord.Color.gold())
                        for i in list(settings.keys()):
                            set_embed.add_field(name=i,value=settings[i],inline=False)
                        set_embed.set_footer(text='DungeonBot Settings')
                        await client.send_message(m.channel, embed=set_embed)
                    else:
                        if has_role(m.author, settings['admin-role']):
                            try:
                                settings[command[1][0]] = command[1][1]
                                ret = 'Set ' + command[1][0] + ' to ' + command[1][1]
                            except:
                                ret = 'Invalid setting name'
                        else:
                            ret = 'You must have the ' + settings['admin-role'] + ' role to do that.'
                else:
                    ret = 'Unknown command: `' + command[0] + '`'
                        

            if ret != None:
                await client.send_message(m.channel, space_remove(ret))
        except IndexError:
            await client.send_message(m.channel, 'Not enough args')
        except SyntaxError:
            await client.send_message(m.channel, 'Error - ' + str(sys.exc_info()[0]))
    for user in m.mentions:
        if user.id == client.user.id:
            syn_embed = discord.Embed(title='Help', color=discord.Color.gold())
            syn_embed.add_field(name='Basic Syntax Help:',value='- Start every command with "' + settings['prefix'] + '"\n' +
                                      '- Separate command arguments with spaces\n' +
                                      '---------------------------------------------\n' +
                                      'Commands (do ?help <command> for specific info on that command):')
            for cmd in list(cmd_help.keys()):
                syn_embed.add_field(value=cmd_help[cmd], name=cmd)
            syn_embed.set_footer(text='DungeonBot Help Docs')
            await client.send_message(m.channel,embed=syn_embed)
    settings_ent[m.server.name] = settings
    set_f = open('settings.cfg', 'w')
    set_f.write(str(settings_ent))
    set_f.close()
    await client.change_presence(game=discord.Game(name=settings_ent['_global_']['game-status']))
@client.event
async def on_member_join(m):
    global settings_ent
    settings = settings_ent[m.server.name]
    await client.send_message(m, 'Hi, ' + m.name + '! ' + settings['welcome-message'] + ' For help with my commands, go to the server and type "' + settings['prefix'] + 'help"!')
    
client.run('lol')
